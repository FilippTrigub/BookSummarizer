import 'package:test_stacked_web_app/ui/common/app_colors.dart';
import 'package:flutter/material.dart';

class DynamicForm extends StatefulWidget {
  const DynamicForm({Key? key}) : super(key: key);

  @override
  DynamicFormState createState() => DynamicFormState();
}

class DynamicFormState extends State<DynamicForm> {
  final List<TextEditingController> _controllers = [];

  void addPartDelimiterField() {
    setState(() {
      _controllers.add(TextEditingController());
    });
  }

  List<String> getPartDelimiters() {
    return _controllers.map((controller) => controller.text).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        MaterialButton(
          onPressed: addPartDelimiterField,
          color: kcDarkGreyColor,
          child: const Text('Add part'),
          textColor: Colors.white,
        ),
        const SizedBox(
          height: 5,
        ),
        for (var controller in _controllers)
          TextField(controller: controller),
          const SizedBox(
            height: 5,
          ),
      ],
    );
  }
}
