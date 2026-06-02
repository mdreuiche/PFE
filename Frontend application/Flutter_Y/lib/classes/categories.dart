import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class Cate {
  final String name;
  final String description;

  Cate({required this.name, required this.description});

  factory Cate.fromJson(Map<String, dynamic> json) {
    return Cate(
      name: json['category_name'],
      description: json['category_description'],
    );
  }
}

Future<List<Cate>?> fetchCategories(BuildContext context) async {
  final prefs = await SharedPreferences.getInstance();
  final accessToken = prefs.getString('access_token');

  if (accessToken == null) {
    print('getCategories: No access token found');
    Navigator.pushReplacementNamed(context, '/login');
    return null;
  }
  final url = Uri.parse('http://192.168.1.108:8000/user-categories/');
  final response = await http.get(
    url,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
  );

  if (response.statusCode == 200) {
    List<dynamic> data = json.decode(response.body);
    print('getCategories: Data fetched successfully: $data');
    return data.map((item) => Cate.fromJson(item)).toList();
  } else if (response.statusCode == 401) {
    print('getCategories: Access token expired, refreshing...');
    await _refreshToken(context);
  } else {
    print('getCategories: Failed to load categories: ${response.statusCode}');
    throw Exception('Failed to load categories: ${response.statusCode}');
  }
  return null;
}

// Wrapper function to convert List<Cate> to List<dynamic>
Future<List<dynamic>?> fetchCategoriesAsDynamic(BuildContext context) async {
  final categories = await fetchCategories(context);
  return categories?.map((category) => category as dynamic).toList();
}

// Pass the context to the _refreshToken method to handle navigation
Future<void> _refreshToken(BuildContext context) async {
  final prefs = await SharedPreferences.getInstance();
  final refreshToken = prefs.getString('refresh_token');

  if (refreshToken == null) {
    Navigator.pushReplacementNamed(context, '/login');
    return;
  }

  final url = Uri.parse('http://127.0.0.1:8000/token/refresh/');
  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'refresh': refreshToken}),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      await prefs.setString('access_token', data['access']);
      await fetchCategories(context); // Re-fetch categories
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Session expired. Please log in again.')),
      );
      Navigator.pushReplacementNamed(context, '/login');
    }
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('An error occurred: $e')),
    );
    Navigator.pushReplacementNamed(context, '/login');
  }
}



// Get Category Usinf Service Name.
Future<List<Cate>?> getCategories(BuildContext context, int id) async {
  final prefs = await SharedPreferences.getInstance();
  final accessToken = prefs.getString('access_token');

  if (accessToken == null) {
    print('getCategories: No access token found');
    Navigator.pushReplacementNamed(context, '/login');
    return null;
  }

  final url = Uri.parse('http://192.168.1.108:8000/user-categories/');
  final response = await http.get(
    url,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
  );

  if (response.statusCode == 200) {
    List<dynamic> data = json.decode(response.body); // Assuming response is a List
    print('getCategories: Data fetched successfully: $data');


    print('getCategories: Data fetched successfully: $data');
    return data.map((item) => Cate.fromJson(item)).toList();
  } else if (response.statusCode == 401) {
    print('getCategories: Access token expired, refreshing...');
    await _refreshToken(context);
  } else {
    print('getCategories: Failed to load categories: ${response.statusCode}');
    throw Exception('Failed to load categories: ${response.statusCode}');
  }

  return null;
}
