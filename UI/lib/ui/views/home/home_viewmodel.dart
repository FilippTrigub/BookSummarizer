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
import 'package:file_picker/file_picker.dart';
import 'dart:io';


class HomeViewModel extends BaseViewModel {
  BuildContext? _context;
  bool get isContextSet => _context != null;

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
      'email': emailController.text,
      'name': nameController.text,
      'delimiters': partDelimiters,
      'file_path': pickedFilePath
    });

    var response = await request.send();

    if (response.statusCode == 200) {
      print('Summarization successful');
      resetAllFields();
      if (_context != null) {
        showCheckmarkOverlay(_context!);
      }
    } else {
      print('Summarization failed with status: ${response.statusCode}.');
    }
  }

  void resetAllFields() {
  titleController.clear();
  descriptionController.clear();
  emailController.clear();
  nameController.clear();
  pickedFilePath = null;
  pickedFileName = null;
  notifyListeners();  // Notify listeners to rebuild UI
  }

  void showCheckmarkOverlay(BuildContext context) {
  OverlayEntry overlayEntry = OverlayEntry(
    builder: (context) => const Stack(
      children: <Widget>[
        Opacity(
          opacity: 0.8,
          child: ModalBarrier(
            dismissible: false,
            color: Colors.black,
          ),
        ),
        Center(
          child: Icon(
            Icons.check_circle,
            color: Colors.green,
            size: 100.0,
          ),
        ),
      ],
    ),
  );

  Overlay.of(context)!.insert(overlayEntry);

  // Remove the overlay after 3 seconds
  Future.delayed(const Duration(seconds: 3), () {
    overlayEntry.remove();
    });
  }


  FilePickerResult? filePickerResult;
  File? pickedFilePath;
  String? pickedFileName;
  bool _isLoading = false;

  bool get isLoading => _isLoading;

  pickAudioFile(context) async {
      try {
      _isLoading = true;
      notifyListeners();
      
      filePickerResult = await FilePicker.platform.pickFiles(
        type: FileType.audio,
        allowMultiple: false,
      );

      if (filePickerResult != null) {
        pickedFilePath = File(filePickerResult!.files.single.bytes.toString());
        pickedFileName = filePickerResult!.files.single.name;
        notifyListeners();
        print('$pickedFileName');
      }
      
      _isLoading = false;
      _context = context;
      notifyListeners();
    } 
    catch(e) {
        print(e);
    }
  }
}
