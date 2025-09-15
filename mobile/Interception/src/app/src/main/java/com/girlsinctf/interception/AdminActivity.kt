package com.girlsinctf.interception

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.dimensionResource
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.girlsinctf.interception.ui.theme.InterceptionTheme
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import org.json.JSONObject

class AdminActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val adminKey = intent.getStringExtra("ADMIN_KEY")

        enableEdgeToEdge()
        setContent {
            InterceptionTheme {
                if (adminKey == getString(R.string.admin_key)) {
                    AdminApp()
                } else {
                    AccessDeniedScreen()
                }
            }
        }
    }
}

@Composable
fun AccessDeniedScreen() {
    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "Access Denied",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdminApp() {
    var result by remember { mutableStateOf("Check that our servers are running OK!") }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Text(
                        text = "Admin Panel",
                        fontWeight = FontWeight.Bold
                    )
                },
                colors = TopAppBarDefaults.largeTopAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { innerPadding ->
        Surface(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(MaterialTheme.colorScheme.tertiaryContainer),
            color = MaterialTheme.colorScheme.background
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Image(
                    painter = painterResource(R.drawable.catadmin),
                    contentDescription = "Admin Cat",
                    modifier = Modifier
                        .width(dimensionResource(R.dimen.image_width))
                        .height(dimensionResource(R.dimen.image_height))
                )

                Spacer(modifier = Modifier.height(24.dp))

                Button(
                    onClick = {
                        CoroutineScope(Dispatchers.IO).launch {
                            val response = runHealthcheck("127.0.0.1")
                            result = response
                        }
                    }
                ) {
                    Text("Run")
                }

                Spacer(modifier = Modifier.height(24.dp))

                // Result text
                Text(
                    text = result,
                    style = MaterialTheme.typography.bodyLarge,
                    modifier = Modifier.padding(8.dp)
                )
            }
        }
    }
}

fun runHealthcheck(hostname: String): String {
    val client = OkHttpClient()
    // Update API URL for challenge server!
    val apiUrl = "http://178.128.30.243:3000/admin/healthcheck"

    val json = JSONObject().apply {
        put("hostname", hostname)
    }

    val body = json.toString()
        .toRequestBody("application/json; charset=utf-8".toMediaTypeOrNull())

    val request = Request.Builder()
        .url(apiUrl)
        .post(body)
        .build()

    return try {
        client.newCall(request).execute().use { response: Response ->
            if (!response.isSuccessful) {
                "Error: ${response.code}"
            } else {
                val respBody = response.body?.string() ?: "No response body"
                val respJson = JSONObject(respBody)
                respJson.getString("data")
            }
        }
    } catch (e: Exception) {
        "Exception: ${e.message}"
    }
}
