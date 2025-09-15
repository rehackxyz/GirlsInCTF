package com.girlsinctf.popcat

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.media.SoundPool
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.dimensionResource
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.girlsinctf.popcat.ui.theme.PopCatTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            PopCatTheme {
                PopcatApp()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PopcatApp() {

    var isClicked by remember { mutableStateOf(false) }
    var clickCount by remember { mutableStateOf(0) }

    val context = LocalContext.current
    val soundPool = remember { SoundPool.Builder().setMaxStreams(5).build() }
    val popSoundId = remember { soundPool.load(context, R.raw.pop, 1) }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Text(
                        text = "PopCat",
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
                modifier = Modifier.fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Top
            ) {
                Text(
                    text = "IT'S OVER 9000!!! \uD83D\uDE40",
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Bold,
                    fontSize = 30.sp,
                    modifier = Modifier.padding(16.dp)
                )
                Spacer(modifier = Modifier.height(dimensionResource(R.dimen.padding_vertical)))

                PopcatTextAndImage(
                    drawableResourceId = if (isClicked) R.drawable.cat_open else R.drawable.cat_close,
                    counterValue = clickCount,
                    onImageClick = {
                        clickCount++
                        isClicked = true
                        soundPool.play(popSoundId, 1f, 1f, 1, 0, 1f)
                        // return to closed state after delay
                        android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                            isClicked = false
                        }, 200)
                    }
                )
            }
        }
        var winDialog by remember { mutableStateOf(false) }

        if (clickCount >= 999999999) {
            winDialog = true;
        }

        if (winDialog) {
            val flag = FlagProvider.getFlag(context)
            AlertDialog (
                onDismissRequest = {},
                title = { Text("Congratulations!") },
                text = { Text(flag)},
                confirmButton = {
                    TextButton(onClick = {
                        winDialog = false
                        clickCount = 0
                    }) {
                        Text("OK")
                    }
                },
                dismissButton = {
                    TextButton(
                        onClick = {
                            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                            val clip = ClipData.newPlainText("flag", flag)
                            clipboard.setPrimaryClip(clip)
                        }
                    ) {
                        Text("Copy")
                    }
                }
            )
        }
    }
}

@Composable
fun PopcatTextAndImage(
    drawableResourceId: Int,
    counterValue: Int,
    onImageClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = modifier.fillMaxSize()
        ) {
            Image(
                painter = painterResource(drawableResourceId),
                contentDescription = stringResource(R.string.content_description),
                modifier = Modifier
                    .width(dimensionResource(R.dimen.button_image_width))
                    .height(dimensionResource(R.dimen.button_image_height))
                    .clickable { onImageClick() }
            )
            Spacer(modifier = Modifier.height(dimensionResource(R.dimen.padding_vertical)))
            Text(
                text = "$counterValue / 999999999",
                style = MaterialTheme.typography.bodyMedium,
                fontSize = 16.sp
            )
        }
    }
}

@Preview
@Composable
fun PopcatPreview() {
    PopCatTheme {
        PopcatApp()
    }
}
