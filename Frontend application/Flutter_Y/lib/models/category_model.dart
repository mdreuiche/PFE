import 'package:flutter/material.dart';

class CategoryModel {
  String name;
  String iconPath;
  Color boxColor;

  CategoryModel({
    required this.name,
    required this.iconPath,
    required this.boxColor,
  });

  static List<CategoryModel> getCategories(){
    List<CategoryModel> categories =[];

  categories.add(
    CategoryModel(
     name: 'Health',
     iconPath: 'assets/icons/pie.svg',
     boxColor: const Color.fromARGB(92, 198, 136, 242)
    )
  );
  categories.add(
    CategoryModel(
     name: 'Home',
     iconPath: 'assets/icons/pie.svg',
     boxColor: const Color.fromARGB(92, 93, 13, 150)
    )
  );

 categories.add(
    CategoryModel(
     name: 'Education',
     iconPath: 'assets/icons/pie.svg',
     boxColor: const Color.fromARGB(92, 48, 137, 167)
    )
  );

  categories.add(
    CategoryModel(
     name: 'Transport',
     iconPath: 'assets/icons/pie.svg',
     boxColor: const Color.fromARGB(92, 48, 167, 105)
    )
  );

    return categories;
  }
}