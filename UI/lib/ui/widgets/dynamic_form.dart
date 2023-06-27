import 'package:test_stacked_web_app/ui/common/app_colors.dart';
import 'package:flutter/material.dart';

class DynamicForm extends StatefulWidget {
  final Function(List<TextEditingController>) onControllersChanged;

  const DynamicForm({Key? key, required this.onControllersChanged}) : super(key: key);

  @override
  DynamicFormState createState() => DynamicFormState();
}

class DynamicFormState extends State<DynamicForm> {
  final List<TextEditingController> _controllers = [];

  void addPartDelimiterField() {
    var controller = TextEditingController();
    controller.addListener(() {
      widget.onControllersChanged(_controllers);
    });

    setState(() {
      _controllers.add(controller);
    });
  }

  void removePartDelimiterField() {
    if (_controllers.isNotEmpty) {
      setState(() {
        _controllers.removeLast();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return DynamicFormInheritedWidget(
      formState: this,
      child: Form(
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                MaterialButton(
                  onPressed: addPartDelimiterField,
                  color: kcDarkGreyColor,
                  child: const Text('Add part'),
                  textColor: Colors.white,
                ),
                const SizedBox(width: 10),
                MaterialButton(
                  onPressed: _controllers.isNotEmpty ? removePartDelimiterField : null,
                  color: kcDarkGreyColor,
                  disabledColor: Colors.grey,
                  child: const Text('Remove part'),
                  textColor: Colors.white,
                ),
              ],
            ),
            const SizedBox(
              height: 5,
            ),
            for (var controller in _controllers)
              TextFormField(
                controller: controller,
                validator: (value) {
                  // Add your validation logic here
                  return null;
                },
                textAlign: TextAlign.center,
              ),
            const SizedBox(
              height: 5,
            ),
          ],
        ),
      ),
    );
  }
}



class DynamicFormInheritedWidget extends InheritedWidget {
  final DynamicFormState formState;

  DynamicFormInheritedWidget({
    Key? key,
    required this.formState,
    required Widget child,
  }) : super(key: key, child: child);

  @override
  bool updateShouldNotify(DynamicFormInheritedWidget oldWidget) {
    return oldWidget.formState != formState;
  }

  static DynamicFormInheritedWidget? of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<DynamicFormInheritedWidget>();
  }
}
