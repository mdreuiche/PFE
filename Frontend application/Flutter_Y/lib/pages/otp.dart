import 'package:flutter/material.dart';
import 'package:easelink/pages/newpassword.dart';

//For this
import 'package:dio/dio.dart';


// you need to add this:
//                 dio: ^5.0.3
// if you are using the version that i pushed, you just need to reload the yaml file for installing nessecary Libraries.


class OtpScreen extends StatefulWidget {
  final String email;

  const OtpScreen({super.key, required this.email});

  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  final TextEditingController _otpController = TextEditingController();
  final Dio _dio = Dio();
  bool _isLoading = false;

  Future<void> _verifyOtp() async {
    final otp = _otpController.text.trim();

    if (otp.isEmpty || otp.length != 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid 6-digit OTP.')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final response = await _dio.post(
        'http://192.168.1.108:8000/password-reset/verify-otp/',
        data: {
          'email': widget.email,
          'otp': otp,
        },
      );

      if (response.statusCode == 200) {
        // Handle successful OTP verification (e.g., navigate to the next screen)
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => NewPasswordPage(email: widget.email),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(response.data['message'] ?? 'OTP verification failed.')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('An error occurred. Please try again.')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,

      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,

          children: [
            Image.asset(
                    'assets/images/otp.png',
                    height: 150,
                  ),
            Text(
              'Enter the OTP sent to ${widget.email}',
              style: TextStyle(
                      fontSize: 30,
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            
            

            TextField(
              controller: _otpController,
              keyboardType: TextInputType.number,
              maxLength: 6,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'OTP',
                prefixIcon: Icon(Icons.password_sharp),
              ),
            ),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: _isLoading ? null : _verifyOtp,
                  style: ElevatedButton.styleFrom(
                            backgroundColor: Color.fromARGB(255, 240, 58, 3),
                            foregroundColor: Colors.white,
                            padding: EdgeInsets.symmetric(
                                horizontal: 80, vertical: 15),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
              child: _isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text('Verify'),
            ),
          ],
        ),
      ),
    );
  }
}

