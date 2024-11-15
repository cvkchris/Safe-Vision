import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:video_player/video_player.dart';
import 'package:flutter_mjpeg/flutter_mjpeg.dart';

void main() {
  runApp(SafeVisionApp());
}

/// The main application widget for SafeVision.
class SafeVisionApp extends StatelessWidget {
  const SafeVisionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SafeVision',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        textTheme: TextTheme(
          bodyLarge: TextStyle(color: Colors.white),
        ),
        appBarTheme: AppBarTheme(
          color: Colors.deepPurple, // Deep purple theme for AppBar
          elevation: 5.0,
          titleTextStyle: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
      ),
      home: SafeVisionHomePage(),
    );
  }
}

/// The home page of the SafeVision app with options for video prediction and live stream.
class SafeVisionHomePage extends StatefulWidget {
  const SafeVisionHomePage({super.key});

  @override
  _SafeVisionHomePageState createState() => _SafeVisionHomePageState();
}

class _SafeVisionHomePageState extends State<SafeVisionHomePage> {
  final ImagePicker _picker = ImagePicker();

  /// Function to pick a video from the gallery and navigate to the prediction page.
  Future<void> _pickVideo(BuildContext context) async {
    final XFile? video = await _picker.pickVideo(source: ImageSource.gallery);
    if (video != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => PredictionPage(videoFile: File(video.path)),
        ),
      );
    }
  }

  /// Function to navigate to the live stream page.
  Future<void> _startLiveStream(BuildContext context) async {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LiveStreamPage(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('SafeVision'),
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.blue, Colors.purple],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Text(
                'Safe Vision',
                style: TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              Text(
                'The watchful eye',
                style: TextStyle(
                  fontSize: 18,
                  color: Colors.white70,
                  fontStyle: FontStyle.italic,
                ),
              ),
              SizedBox(height: 50), // Space between header and buttons
              ElevatedButton.icon(
                icon: Icon(Icons.video_library, size: 30),
                onPressed: () => _pickVideo(context),
                label: Text(
                  'Pick a Video for Prediction',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  elevation: 5,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              SizedBox(height: 30),
              ElevatedButton.icon(
                icon: Icon(Icons.live_tv, size: 30),
                onPressed: () => _startLiveStream(context),
                label: Text(
                  'Start Live Stream',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  elevation: 5,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}



/// Prediction page that plays the selected video and displays the prediction result.
class PredictionPage extends StatefulWidget {
  final File videoFile;

  const PredictionPage({super.key, required this.videoFile});

  @override
  _PredictionPageState createState() => _PredictionPageState();
}

class _PredictionPageState extends State<PredictionPage> {
  late VideoPlayerController _controller;
  String _predictionResult = 'Processing...';
  bool _isPlaying = false;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.file(widget.videoFile)
      ..initialize().then((_) {
        setState(() {
          _controller.play();
        });
      });
    _uploadVideo(widget.videoFile);
  }

  /// Uploads the selected video to the Flask API and retrieves the prediction result.
  Future<void> _uploadVideo(File videoFile) async {
    var url = Uri.parse('http://10.0.2.2:5000/api/upload');
    var request = http.MultipartRequest('POST', url);
    var video = await http.MultipartFile.fromPath('file', videoFile.path);
    request.files.add(video);

    var response = await request.send();
    if (response.statusCode == 200) {
      final responseData = await http.Response.fromStream(response);
      final data = json.decode(responseData.body);
      setState(() {
        _predictionResult = data['prediction'] ?? 'No prediction data';
      });
    } else {
      setState(() {
        _predictionResult = 'Error uploading video';
      });
    }
  }

  void _togglePlayPause() {
    setState(() {
      if (_isPlaying) {
        _controller.pause();
      } else {
        _controller.play();
      }
      _isPlaying = !_isPlaying;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Prediction Result'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (_controller.value.isInitialized)
              AspectRatio(
                aspectRatio: _controller.value.aspectRatio,
                child: VideoPlayer(_controller),
              ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _togglePlayPause,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepPurple,
                foregroundColor: Colors.white,
                padding: EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                elevation: 5,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: Text(
                _isPlaying ? 'Pause' : 'Play',
                style: TextStyle(fontSize: 18),
              ),
            ),
            SizedBox(height: 20),
            Text(
              'Prediction Result: $_predictionResult',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

/// Live stream page that displays real-time prediction results from the camera feed.
class LiveStreamPage extends StatefulWidget {
  const LiveStreamPage({super.key});

  @override
  _LiveStreamPageState createState() => _LiveStreamPageState();
}

class _LiveStreamPageState extends State<LiveStreamPage> {
  String _predictionResult = 'Awaiting response...';
  bool isStreaming = false;

  @override
  void initState() {
    super.initState();
    _startLiveStream();
  }

  // Start live video stream by calling Flask MJPEG stream
  Future<void> _startLiveStream() async {
    var url = Uri.parse('http://10.0.2.2:5000/api/video_feed');
    var response = await http.get(url).timeout(Duration(seconds: 20));

    if (response.statusCode == 200) {  
      setState(() {
        isStreaming = true;
        _fetchPrediction();
      });
    }
  }

  // Fetch predictions at intervals
  Future<void> _fetchPrediction() async {
    var url = Uri.parse('http://10.0.2.2:5000/api/live_prediction');
    var response = await http.get(url).timeout(Duration(seconds: 20));

    if (response.statusCode == 200 ) {  
      final data = json.decode(response.body);
      setState(() {
        _predictionResult = 'Live Prediction: ${data['status']}';
      });
    }
  }

  // Stop live stream and cancel prediction polling
  Future<void> _stopLiveStream() async {
    var url = Uri.parse('http://10.0.2.2:5000/api/stop_camera');
    if (mounted) {
        var response = await http.post(url);
        if (response.statusCode == 204) {  // Check for 204 No Content status
          setState(() {
            isStreaming = false;
            _predictionResult = 'Live stream stopped';
          });
        
      }
    }
  }

  

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Live Stream'),
      ),
      body: Stack(
        alignment: Alignment.center,
        children: [
          // MJPEG video stream widget
          Mjpeg(
            isLive: true,
            stream: 'http://10.0.2.2:5000/api/video_feed',
          ),
          // Overlay prediction result
          Positioned(
            bottom: 20,
            child: Container(
              color: Colors.black54,
              padding: EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              child: Text(
                _predictionResult,
                style: TextStyle(color: Colors.white, fontSize: 18),
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Button for fetching predictions
          FloatingActionButton(
            onPressed: _startLiveStream,
            heroTag: 'fetchPrediction',
            tooltip: 'Refresh',
            child: Icon(Icons.refresh),
          ),
          SizedBox(height: 10), // Space between buttons
          // Button for stopping the live stream
          FloatingActionButton(
            onPressed: _stopLiveStream,
            heroTag: 'stopStream',
            tooltip: 'Stop Live Stream',
            child: Icon(Icons.stop_circle_rounded),
          ),
        ],
      ),
    );
  }
}

