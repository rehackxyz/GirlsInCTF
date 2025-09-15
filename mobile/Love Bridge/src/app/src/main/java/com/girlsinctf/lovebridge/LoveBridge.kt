package com.girlsinctf.lovebridge

class LoveBridge {
    external fun encrypt(string: String): String
    external fun decrypt(string: String): String

    companion object {
        // Used to load the 'lovebridge' library on application startup.
        init {
            System.loadLibrary("lovebridge")
        }
    }
}