import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_soloud/flutter_soloud.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Initialize the player
  await SoLoud.instance.init();
  runApp(const MyApp());
}

String getFlag() {
  List<int> ciphertext = [5,1,22,4,112,119,57,36,46,55,22,22,113,48,29,47,118,41,113,119,29,22,42,115,44,5,49,29,42,118,48,38,113,48,63];

  String flag = "";
  for (int i = 0; i < ciphertext.length; i++) {
    flag += String.fromCharCode(ciphertext[i] ^ 0x42);
  }
  return flag;
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PopCat Revenge',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.purple.shade500),
      ),
      home: const MyHomePage(title: 'PopCat Revenge'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;
  bool _isClicked = false;
  AudioSource? popSound;
  Timer? revertTimer;

  @override
  void initState() {
    super.initState();

    () async {
      popSound = await SoLoud.instance.loadAsset('assets/pop.mp3');
    }();
  }

  void _incrementCounter() async {
    setState(() {
      _counter++;
      _isClicked = !_isClicked;
    });

    revertTimer?.cancel();
    await SoLoud.instance.play(popSound!);
    // start timer to revert back to default face after 5ms
    revertTimer = Timer(Duration(milliseconds: 200), () {
      setState(() {
        _isClicked = false;
      });
    });

    // Check win condition
    if (_counter >= 999999999) {
      _showFlagDialog();
    }
  }

  void _showFlagDialog() {
    String flag = getFlag();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('You win! 🤩'),
          content: Text('Here is your flag! $flag'),
          actions: [
            TextButton(
              onPressed: () {
                Clipboard.setData(ClipboardData(text: flag));
              },
              child: const Text('Copy to clipboard'),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text("OK"),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    revertTimer?.cancel();
    SoLoud.instance.deinit();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
        centerTitle: true,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            GestureDetector(
              onTap: _incrementCounter,
              child: Image(
                image: _isClicked
                    ? AssetImage('assets/cat_open.png')
                    : AssetImage('assets/cat_close.png'),
                width: 256,
                height: 256,
              ),
            ),
            Text(
              '$_counter / 999999999',
              style: Theme.of(context).textTheme.headlineLarge,
            ),
          ],
        ),
      ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }
}
