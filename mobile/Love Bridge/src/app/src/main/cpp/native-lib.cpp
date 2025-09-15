#include <jni.h>
#include <string>
#include <vector>
#include <cstdint>

// ---------- utils ----------
static inline uint8_t bit_reverse(uint8_t b){
    uint8_t r=0;
    for(int i=0;i<8;i++) if(b&(1u<<i)) r|=1u<<(7-i);
    return r;
}

// Base64 (compact, ASCII-safe)
static const char B64TAB[]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
static std::string b64enc(const std::vector<uint8_t>& in){
    std::string out; out.reserve(((in.size()+2)/3)*4);
    int val=0, valb=-6;
    for(uint8_t c: in){
        val=(val<<8)+c; valb+=8;
        while(valb>=0){ out.push_back(B64TAB[(val>>valb)&0x3F]); valb-=6; }
    }
    if(valb>-6) out.push_back(B64TAB[((val<<8)>>(valb+8))&0x3F]);
    while(out.size()%4) out.push_back('=');
    return out;
}
static std::vector<uint8_t> b64dec(const std::string& s){
    std::vector<int> T(256,-1); for(int i=0;i<64;i++) T[(unsigned char)B64TAB[i]]=i;
    std::vector<uint8_t> out; out.reserve((s.size()*3)/4);
    int val=0, valb=-8;
    for(unsigned char c: s){
        if(c=='=') break;
        int v = T[c]; if(v<0) continue; // skip whitespace/invalid
        val=(val<<6)+v; valb+=6;
        if(valb>=0){ out.push_back(uint8_t((val>>valb)&0xFF)); valb-=8; }
    }
    return out;
}

// ---------- pairwise mixing (and exact inverse) ----------
static void mix_forward(std::vector<uint8_t>& buf){
    for(int i=0;i<8;i++){
        for(size_t j=0;j+1<buf.size(); j+=2){
            uint8_t v4 = buf[j+1];
            int shift = i % 5;
            int right = shift ? (v4 >> (8-shift)) : 0;
            int left  = (v4 << shift) & 0xFF;
            uint8_t v3 = (buf[j] ^ ((55*i)&0xFF) ^ right ^ left) & 0xFF;
            buf[j]=v4; buf[j+1]=v3;
        }
    }
}
static void mix_inverse(std::vector<uint8_t>& buf){
    for(int i=7;i>=0;i--){
        for(int j=(int)buf.size()-2; j>=0; j-=2){
            uint8_t new_v3 = buf[j+1];
            uint8_t new_v4 = buf[j];
            int shift = i % 5;
            int right = shift ? (new_v4 >> (8-shift)) : 0;
            int left  = (new_v4 << shift) & 0xFF;
            uint8_t old_v0 = (new_v3 ^ ((55*i)&0xFF) ^ right ^ left) & 0xFF;
            buf[j]=old_v0; buf[j+1]=new_v4;
        }
    }
}

// ---------- TEA (standard, 32 rounds) ----------
static inline void tea_enc(uint32_t v[2], const uint32_t k[4]){
    uint32_t v0=v[0], v1=v[1], sum=0, delta=0x9E3779B9;
    for(int i=0;i<32;i++){
        sum += delta;
        v0 += ((v1<<4)+k[0]) ^ (v1+sum) ^ ((v1>>5)+k[1]);
        v1 += ((v0<<4)+k[2]) ^ (v0+sum) ^ ((v0>>5)+k[3]);
    }
    v[0]=v0; v[1]=v1;
}
static inline void tea_dec(uint32_t v[2], const uint32_t k[4]){
    uint32_t v0=v[0], v1=v[1], delta=0x9E3779B9, sum=delta*32;
    for(int i=0;i<32;i++){
        v1 -= ((v0<<4)+k[2]) ^ (v0+sum) ^ ((v0>>5)+k[3]);
        v0 -= ((v1<<4)+k[0]) ^ (v1+sum) ^ ((v1>>5)+k[1]);
        sum -= delta;
    }
    v[0]=v0; v[1]=v1;
}

// pack/unpack little-endian 8-byte blocks (partial ok, no padding)
static inline void pack_block(const std::vector<uint8_t>& b, size_t off, uint32_t v[2]){
    v[0]=v[1]=0;
    for(int k=0;k<4;k++) if(off+k<b.size())     v[0] |= uint32_t(b[off+k])     << (8*k);
    for(int k=0;k<4;k++) if(off+4+k<b.size())   v[1] |= uint32_t(b[off+4+k])   << (8*k);
}
static inline void unpack_block(std::vector<uint8_t>& b, size_t off, const uint32_t v[2]){
    for(int k=0;k<4;k++) if(off+k<b.size())     b[off+k]   = uint8_t((v[0]>>(8*k))&0xFF);
    for(int k=0;k<4;k++) if(off+4+k<b.size())   b[off+4+k] = uint8_t((v[1]>>(8*k))&0xFF);
}

// ---------- pipeline (with inner Base64 sanitization) ----------
static std::string encrypt_pipeline_inner_b64(const std::string& utf8){
    // 0) inner Base64 of plaintext so the transform always sees ASCII-safe bytes
    std::vector<uint8_t> buf( b64enc(std::vector<uint8_t>(utf8.begin(), utf8.end())).begin(),
                              b64enc(std::vector<uint8_t>(utf8.begin(), utf8.end())).end() );
    // Avoid double work; compute once
    std::string inner = b64enc(std::vector<uint8_t>(utf8.begin(), utf8.end()));
    buf.assign(inner.begin(), inner.end());

    // 1) pairwise mixing
    mix_forward(buf);

    // 2) TEA over 8-byte chunks
//    const uint32_t key[4]={0xDEADBEEF,0xCAFEBABE,0x12345678,0x87654321};
    const uint32_t key[4]={0x1A2B3C4D,0x5E6FBABE,0x13371337,0x42424242};
    for(size_t j=0;j<buf.size(); j+=8){
        uint32_t v[2]; pack_block(buf,j,v); tea_enc(v,key); unpack_block(buf,j,v);
    }

    // 3) per-byte mask + bit-reverse
    for(size_t k=0;k<buf.size();k++){
        uint8_t mask = uint8_t(((4*k) ^ (k*k) ^ 0xAA) & 0xFF);
        buf[k] = bit_reverse( uint8_t(buf[k] ^ mask) );
    }

    // Outer Base64 to make output jstring-safe
    return b64enc(buf);
}

static std::string decrypt_pipeline_inner_b64(const std::string& outerB64){
    // Outer Base64 decode (transport layer)
    std::vector<uint8_t> buf = b64dec(outerB64);

    // 1) undo per-byte bit-reverse + XOR
    for(size_t k=0;k<buf.size();k++){
        uint8_t mask = uint8_t(((4*k) ^ (k*k) ^ 0xAA) & 0xFF);
        buf[k] = uint8_t(bit_reverse(buf[k]) ^ mask);
    }

    // 2) TEA decrypt over 8-byte chunks
    const uint32_t key[4]={0x1A2B3C4D,0x5E6FBABE,0x13371337,0x42424242};
    for(size_t j=0;j<buf.size(); j+=8){
        uint32_t v[2]; pack_block(buf,j,v); tea_dec(v,key); unpack_block(buf,j,v);
    }

    // 3) inverse mixing
    mix_inverse(buf);

    // 4) inner Base64 decode to recover original UTF-8 plaintext
    std::string inner(buf.begin(), buf.end());
    std::vector<uint8_t> plain = b64dec(inner);
    return std::string(plain.begin(), plain.end());
}

// ---------- JNI wrappers ----------
extern "C" JNIEXPORT jstring JNICALL
Java_com_girlsinctf_lovebridge_LoveBridge_encrypt(JNIEnv* env, jobject /*thiz*/, jstring string){
    const char* in = env->GetStringUTFChars(string, nullptr);
    std::string out = encrypt_pipeline_inner_b64(in);
    env->ReleaseStringUTFChars(string, in);
    return env->NewStringUTF(out.c_str());  // ASCII Base64 ciphertext
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_girlsinctf_lovebridge_LoveBridge_decrypt(JNIEnv* env, jobject /*thiz*/, jstring string){
    const char* in = env->GetStringUTFChars(string, nullptr);
    std::string out = decrypt_pipeline_inner_b64(in);
    env->ReleaseStringUTFChars(string, in);
    return env->NewStringUTF(out.c_str());  // original UTF-8 plaintext
}
