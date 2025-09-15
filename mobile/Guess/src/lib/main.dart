import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:guess/utils.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Guess',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const MyHomePage(title: 'Guess'),
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
  final TextEditingController _controller = TextEditingController();
  int _counter = 0;
  int _remaining = 10;

  void _makeGuess() {
    final magicString = generateMagicString();
    final userInput = _controller.text.trim();

    if (userInput == magicString) {
      setState(() {
        _counter++;
        _remaining--;
      });
      _showDialog(
        context,
        'You guessed it! Now just guess $_remaining more times',
      );
    } else {
      _counter = 0;
      _remaining = 10;
      _showDialog(context, 'Try harder 😜');
    }

    if (_counter >= 10 && _remaining == 0) {
      _showFlagDialog();
      // reset count
      _counter = 0;
      _remaining = 10;
    }
  }

  void _showDialog(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(milliseconds: 500),
      ),
    );
  }

  void _showFlagDialog() {
    String flag = getFlag();
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('You win! 🤩'),
          content: Text(flag),
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
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
        centerTitle: true,
      ),
      body: Center(
        child: SingleChildScrollView(
          physics: NeverScrollableScrollPhysics(),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Image(image: AssetImage('assets/catsmirk.png')),
              const Text('Just guess right 10 times :3'),
              SizedBox(
                width: screenWidth * 0.7,
                child: TextField(
                  controller: _controller,
                  decoration: const InputDecoration(labelText: 'Read my mind'),
                ),
              ),
              const SizedBox(height: 30),
              ElevatedButton(
                onPressed: _makeGuess,
                child: const Text('Submit'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
