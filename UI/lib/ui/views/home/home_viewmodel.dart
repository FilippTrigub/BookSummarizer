import 'package:flutter/material.dart';
import 'package:test_stacked_web_app/app/app.bottomsheets.dart';
import 'package:test_stacked_web_app/app/app.dialogs.dart';
import 'package:test_stacked_web_app/app/app.locator.dart';
import 'package:test_stacked_web_app/ui/common/app_constants.dart';
import 'package:test_stacked_web_app/ui/common/app_strings.dart';
import 'package:stacked/stacked.dart';
import 'package:stacked_services/stacked_services.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:test_stacked_web_app/ui/widgets/dynamic_form.dart';


class HomeViewModel extends BaseViewModel {
  final dynamicFormKey = GlobalKey<DynamicFormState>();

  final titleController = TextEditingController();
  final descriptionController = TextEditingController();
  final emailController = TextEditingController();
  final nameController = TextEditingController();

  // No need for dispose() as BaseViewModel does not have it

  final _dialogService = locator<DialogService>();
  final _bottomSheetService = locator<BottomSheetService>();

  String get counterLabel => 'Counter is: $_counter';

  int _counter = 0;

  void incrementCounter() {
    _counter++;
    rebuildUi();
  }

  void showDialog() {
    _dialogService.showCustomDialog(
      variant: DialogType.infoAlert,
      title: 'Get in contact with the GenMyBot team!',
      description: '<ADD FORM>',
    );
  }

  void showBottomSheet() {
    _bottomSheetService.showCustomSheet(
      variant: BottomSheetType.notice,
      title: ksHomeBottomSheetTitle,
      description: ksHomeBottomSheetDescription,
    );
  }

  void runSummarization() async {
    var partDelimiters = dynamicFormKey.currentState?.getPartDelimiters();

    var request = http.Request('POST', Uri.parse(backendEndpoint));
    request.body = json.encode({
      'title': titleController.text,
      'description': descriptionController.text,
      'parts': partDelimiters,
      'email': emailController.text,
      'name': nameController.text,
    });

    var response = await request.send();

    if (response.statusCode == 200) {
      print('Summarization successful');
    } else {
      print('Summarization failed with status: ${response.statusCode}.');
    }
  }
}
