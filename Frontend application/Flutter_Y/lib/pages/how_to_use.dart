import 'package:flutter/material.dart';
import 'welcomePage.dart';

class HowToUsePage extends StatefulWidget {
  const HowToUsePage({super.key});

  @override
  _HowToUsePageState createState() => _HowToUsePageState();
}

class _HowToUsePageState extends State<HowToUsePage> {
  final PageController _pageController = PageController();
  int currentPage = 0;

  // Screens Data (Now includes 'image' path)
  final List<Map<String, String>> screens = [
    {
      "image": "assets/images/screen1.png",
      "title": "Create New Account",
      "description": "Create Your Account to get the full access of our features. Be sure that all your data is secure.",
      "button": "Continue",
    },
    {
      "image": "assets/images/screen2.png",
      "title": "Login to Your Account",
      "description": "Login with your email and password to access your personalized dashboard.",
      "button": "Next",
    },
    {
      "image": "assets/images/screen3.png",
      "title": "Explore Features",
      "description": "Discover amazing features like AI Chat, News Feed, and Anime Store.",
      "button": "Finish",
    },
  ];

  void goToNextPage() {
    if (currentPage < screens.length - 1) {
      _pageController.nextPage(
          duration: Duration(milliseconds: 300), curve: Curves.easeInOut);
    } else {
      print("Tutorial Finished");
      Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => WelcomePage()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Column(
        children: [
          // Page View for Screens
          Expanded(
            child: PageView.builder(
              controller: _pageController,
              itemCount: screens.length,
              onPageChanged: (index) {
                setState(() {
                  currentPage = index;
                });
              },
              itemBuilder: (context, index) {
                return buildScreen(
                  imagePath: screens[index]["image"]!,
                  title: screens[index]["title"]!,
                  description: screens[index]["description"]!,
                  buttonText: screens[index]["button"]!,
                );
              },
            ),
          ),

          // Progress Indicator
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(screens.length, (index) {
              return AnimatedContainer(
                duration: Duration(milliseconds: 300),
                margin: EdgeInsets.symmetric(horizontal: 5),
                height: 10,
                width: currentPage == index ? 20 : 10,
                decoration: BoxDecoration(
                  color:
                      currentPage == index ? const Color.fromARGB(255, 255, 25, 0) : Colors.grey[300],
                  borderRadius: BorderRadius.circular(5),
                ),
              );
            }),
          ),
          SizedBox(height: 10),
        ],
      ),
    );
  }

 Widget buildScreen({
  required String imagePath,
  required String title,
  required String description,
  required String buttonText,
}) {
  return SizedBox(
    height: MediaQuery.of(context).size.height, // Full-screen container
    child: Stack(
      children: [
        // Background Image
        Positioned.fill(
          child: Image.asset(
            imagePath,
            width: double.infinity,
            height: double.infinity,
            fit: BoxFit.cover,
          ),
        ),
        
        // Top Section (Text and Button)
        Positioned(
          bottom: 0, // Position the text container at the bottom of the screen
          left: 0,
          right: 0,
          child: Container(
            height: MediaQuery.of(context).size.height * 0.3, // Top 30% hidden behind the text container
            padding: EdgeInsets.symmetric(horizontal: 20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  const Color.fromARGB(255, 255, 255, 255), // Add semi-transparency for text readability
                  const Color.fromARGB(255, 255, 255, 255),
                ],
              ),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  title,
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: const Color.fromARGB(255, 0, 0, 0)),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 10),
                Text(
                  description,
                  style: TextStyle(fontSize: 14, color: const Color.fromARGB(179, 0, 0, 0)),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: goToNextPage,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color.fromARGB(255, 225, 65, 11),
                    padding: EdgeInsets.symmetric(horizontal: 80, vertical: 15),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: Text(buttonText, style: TextStyle(color: const Color.fromARGB(255, 255, 255, 255))),
                ),
              ],
            ),
          ),
        ),
      ],
    ),
  );
}

}
