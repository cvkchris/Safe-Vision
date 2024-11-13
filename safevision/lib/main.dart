import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:video_player/video_player.dart';
import 'package:chewie/chewie.dart';

void main() {
  runApp(SafeVisionApp());
}

class SafeVisionApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SafeVision',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: SafeVisionHomePage(),
    );
  }
}

class SafeVisionHomePage extends StatefulWidget {
  @override
  _SafeVisionHomePageState createState() => _SafeVisionHomePageState();
}

class _SafeVisionHomePageState extends State<SafeVisionHomePage> {
  final ImagePicker _picker = ImagePicker();
  late VideoPlayerController _controller;
  bool isStreaming = false;
  String _predictionResult = 'No prediction yet';
  String _videoUrl = '';

  // Function to pick a video from the gallery
  Future<void> _pickVideo() async {
    final XFile? video = await _picker.pickVideo(source: ImageSource.gallery);

    if (video != null) {
      _uploadVideo(File(video.path));
    }
  }

  // Function to upload video to Flask API
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
        _videoUrl = 'http://10.0.2.2:5000/uploads/' + data['output_video'];
      });
    } else {
      setState(() {
        _predictionResult = 'Error uploading video';  
      });
    }
  }

  // Function to start live video stream
  Future<void> _startLiveStream() async {
    var url = Uri.parse('http://10.0.2.2:5000/api/video_feed');
    var response = await http.get(url);

    if (response.statusCode == 200) {
      setState(() {
        isStreaming = true;
      });
    }
  }

  // Function to stop live stream
  Future<void> _stopLiveStream() async {
    var url = Uri.parse('http://10.0.2.2:5000/api/stop_camera');
    var response = await http.post(url);

    if (response.statusCode == 200) {
      setState(() {
        isStreaming = false;
      });
    }
  }

  // Function to check live prediction status
  Future<void> _checkLivePredictionStatus() async {
    var url = Uri.parse('http://10.0.2.2:5000/api/live_prediction');
    var response = await http.get(url);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      setState(() {
        _predictionResult = 'Live Prediction: ${data['status']}';
      });
    }
  }

  // Initialize video player controller for uploaded video
  Future<void> _initializeVideoPlayer(String videoUrl) async {
    _controller = VideoPlayerController.network(videoUrl);
    await _controller.initialize();
    setState(() {});
  }

  @override
  void dispose() {
    if (_controller.value.isInitialized) {
      _controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('SafeVision'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: <Widget>[
            // Button to pick video
            ElevatedButton(
              onPressed: _pickVideo,
              child: Text('Pick a Video for Prediction'),
            ),
            SizedBox(height: 20),
            // Display prediction result
            Text(
              'Prediction Result: $_predictionResult',
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 20),
            // Display the video player for uploaded video
            if (_videoUrl.isNotEmpty)
              _controller.value.isInitialized
                  ? Chewie(
                      controller: ChewieController(
                        videoPlayerController: _controller,
                        autoPlay: true,
                        looping: false,
                      ),
                    )
                  : CircularProgressIndicator(),
            SizedBox(height: 20),
            // Button to start live stream
            ElevatedButton(
              onPressed: _startLiveStream,
              child: Text('Start Live Stream'),
            ),
            SizedBox(height: 20),
            // Button to stop live stream
            ElevatedButton(
              onPressed: _stopLiveStream,
              child: Text('Stop Live Stream'),
            ),
            SizedBox(height: 20),
            // Button to check live prediction status
            ElevatedButton(
              onPressed: _checkLivePredictionStatus,
              child: Text('Check Live Prediction Status'),
            ),
            SizedBox(height: 20),
            // Display live streaming feed
            if (isStreaming)
              Expanded(
                child: Image.network(
                  'http://10.0.2.2:5000/api/video_feed',
                  fit: BoxFit.cover,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
