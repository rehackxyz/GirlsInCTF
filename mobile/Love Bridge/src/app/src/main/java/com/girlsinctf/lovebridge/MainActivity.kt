package com.girlsinctf.lovebridge

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.TextView

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val msg = getString(R.string.msg)
        findViewById<TextView>(R.id.txt).text = msg
    }
}

