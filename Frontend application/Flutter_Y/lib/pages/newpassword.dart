import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'login.dart';

class NewPasswordPage extends StatefulWidget {
  final String email;

  const NewPasswordPage({super.key, required this.email});
  @override
  _NewPasswordPageState createState() => _NewPasswordPageState();
}

class _NewPasswordPageState extends State<NewPasswordPage> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();
  bool _isLoading = false;
  String _message = '';

  Future<void> _resetPassword() async {
    final String apiUrl = 'http://192.168.1.108:8000/password-reset/reset/';

    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
        _message = '';
      });

      try {
        final response = await http.post(
          Uri.parse(apiUrl),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'email': widget.email,
            'password': _passwordController.text,
            'confirm_password': _confirmPasswordController.text,
          }),
        );

        if (response.statusCode == 200) {
          setState(() {
            _message = 'Password reset successfully.';
          });
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
            builder: (context) => LogInPage(),
      ),
    );
        } else {
          setState(() {
            _message = 'Error: ${json.decode(response.body)['error']}';
          });
        }
      } catch (e) {
        setState(() {
          _message = 'An error occurred. Please try again.';
        });
      } finally {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your password';
    }
    if (value.length < 6) {
      return 'Password must be at least 6 characters long';
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please confirm your password';
    }
    if (value != _passwordController.text) {
      return 'Passwords do not match';
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Reset Password'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _passwordController,
                decoration: InputDecoration(
                  labelText: 'New Password',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.lock),
                ),
                obscureText: true,
                validator: _validatePassword,
              ),
              SizedBox(height: 20),
              TextFormField(
                controller: _confirmPasswordController,
                decoration: InputDecoration(
                  labelText: 'Confirm Password',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.lock),
                ),
                obscureText: true,
                validator: _validateConfirmPassword,
              ),
              SizedBox(height: 20),
              _isLoading
                  ? CircularProgressIndicator()
                  : ElevatedButton(
                      onPressed: _resetPassword,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color.fromARGB(255, 240, 58, 3),
                        foregroundColor: Colors.white,
                        padding: EdgeInsets.symmetric(horizontal: 80, vertical: 15),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      child: Text(
                        'Reset Password',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
              SizedBox(height: 20),
              Text(
                _message,
                style: TextStyle(color: Colors.red),
              ),
            ],
          ),
        ),
      ),
    );
  }
}