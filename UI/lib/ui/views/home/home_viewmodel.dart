import 'dart:developer';
import 'dart:typed_data';

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

import 'package:logging/logging.dart';

final Logger log = Logger('HomeViewModel');

class HomeViewModel extends BaseViewModel {
  BuildContext? _context;
  bool get isContextSet => _context != null;
  List<String> partDelimiters = [];
  var logger = Logger('MyLogger');

  final dynamicFormKey = GlobalKey<DynamicFormState>();

  final titleController = TextEditingController();
  final descriptionController = TextEditingController();
  final emailController = TextEditingController();
  final nameController = TextEditingController();
  final modelKeyController = TextEditingController();
  final budgetController = TextEditingController();

  final _dialogService = locator<DialogService>();
  final _bottomSheetService = locator<BottomSheetService>();

  String get counterLabel => 'Counter is: $_counter';

  int _counter = 0;

  FilePickerResult? filePickerResult;
  Uint8List? pickedFileBytes;
  String? pickedFileName;
  bool _isLoading = false;

  bool get isLoading => _isLoading;

  void incrementCounter() {
    _counter++;
    rebuildUi();
  }

  void showDialog() {
    _dialogService.showCustomDialog(
      variant: DialogType.infoAlert,
      title: 'Get in contact with the GenMyBot team!',
      description: 'info@genmybot.com',
    );
  }

  void showBottomSheet() {
    _bottomSheetService.showCustomSheet(
      variant: BottomSheetType.notice,
      title: ksHomeBottomSheetTitle,
      description: ksHomeBottomSheetDescription,
    );
  }

  void updateControllers(List<TextEditingController> controllers) {
    partDelimiters = controllers.map((controller) => controller.text).toList();
  }

  Future<void> runSummarization(BuildContext? context) async {
    var response = await http.post(
      Uri.parse(backendEndpoint+'/run_summarization'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: json.encode({
        'title': titleController.text,
        'description': descriptionController.text,
        'name': nameController.text,
        'email': emailController.text,
        'delimiters': partDelimiters,
        'file_name': pickedFileName,
        'model_key': modelKeyController.text,
        'budget': budgetController.text,
      }),
    );

    if (response.statusCode == 200) {
      log.warning('Summarization successful');
      resetAllFields();
      if (_context != null) {
        showCheckmarkOverlay(_context!);
      }
    } else {
      log.warning('Summarization failed with status: ${response.statusCode}.');
    }
  }


  void resetAllFields() {
    titleController.clear();
    descriptionController.clear();
    emailController.clear();
    nameController.clear();
    modelKeyController.clear();
    budgetController.clear();
    pickedFileBytes = null;
    pickedFileName = null;
    notifyListeners();
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

  Future.delayed(const Duration(seconds: 15), () {
    overlayEntry.remove();
    });
  }


  pickAudioFile(context) async {
      try {
      _isLoading = true;
      notifyListeners();
      
      filePickerResult = await FilePicker.platform.pickFiles(
        type: FileType.audio,
        allowMultiple: false,
      );

      if (filePickerResult != null) {
        pickedFileBytes = filePickerResult!.files.single.bytes;
        pickedFileName = filePickerResult!.files.single.name;
        uploadFile(pickedFileBytes!, pickedFileName!);
        notifyListeners();        
      }
      
      _isLoading = false;
      _context = context;
      notifyListeners();
    } 
    catch(e) {
        log.warning(e);
    }
  }

  uploadFile(Uint8List fileBytes, String fileName) async {
    var uri = Uri.parse(backendEndpoint+'/upload');
    var request = http.MultipartRequest('POST', uri)
      ..files.add(http.MultipartFile.fromBytes('file', fileBytes, filename: fileName));
    var response = await request.send();
    if (response.statusCode == 200) {
      log.warning("File upload successful");
    } else {
      log.warning("File upload failed");
    }
  }

  Future<bool> checkBackendAvailability() async {
    try {
      logger.warning('URI: ${backendEndpoint+'/check'}');
      final response = await http.get(Uri.parse(backendEndpoint+'/check'));
      logger.warning('URI: ${backendEndpoint+'/check'}');
      logger.warning('response: ${response.toString()}');
      logger.warning('response.statusCode: ${response.statusCode.toString()}');
      
      return response.statusCode == 200;
    } catch (e) {
      log.warning('Exception: $e');
      return false;
    }
  }
}
