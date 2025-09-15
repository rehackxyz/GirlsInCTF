package com.girlsinctf.popcat

import android.content.Context
import android.util.Base64

object FlagProvider {
    fun getFlag(context: Context): String {
        val f1 = context.getString(R.string.f1)
        val f2 = context.getString(R.string.f2)
        val k1 = "meowmeowmeowmeow".toByteArray()
        val k2 = "meowmeowmeowmeowmeow".toByteArray()
        val c1 = Base64.decode(f1, Base64.DEFAULT)
        val c2 = Base64.decode(f2, Base64.DEFAULT)
        val h1 = ByteArray(c1.size) { i->
            (c1[i].toInt() xor k1[i%k1.size].toInt()).toByte()
        }.reversedArray()
        val h2 = ByteArray(c2.size) { i->
            (c2[i].toInt() xor k2[i%k2.size].toInt()).toByte()
        }.reversedArray()
        return (h1+h2).toString(Charsets.UTF_8)
    }
}