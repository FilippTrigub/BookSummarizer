import 'package:test_stacked_web_app/ui/common/app_colors.dart';
import 'package:test_stacked_web_app/ui/common/app_constants.dart';
import 'package:test_stacked_web_app/ui/common/ui_helpers.dart';
import 'package:flutter/material.dart';
import 'package:stacked/stacked.dart';
import 'home_viewmodel.dart';
import 'package:test_stacked_web_app/ui/widgets/dynamic_form.dart';

class HomeViewMobile extends ViewModelWidget<HomeViewModel> {
  HomeViewMobile({super.key});
  final dynamicFormKey = GlobalKey<DynamicFormState>();

  @override
  Widget build(BuildContext context, HomeViewModel viewModel) {
    String recordingTitleText = 'Provide the title of the recording:';
    String recordingDescriptionText = 'Describe the content to help the AI:';
    String emailText = 'Please provide your email address so that we can send you the summary:';
    String nameText = 'Finally please allow us to address you with your name:';
    String recordingTitleHint = 'Title';
    String recordingDescriptionHint = 'Description';
    String emailHint = 'Email';
    String nameHint = 'Name';

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 25.0),
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.max,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                verticalSpaceLarge,
                Column(
                  children: [
                    const Text(
                      'Summarize you recordings!',
                      style: TextStyle(
                        fontSize: 35,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(
                      height: 50,
                    ),
                    ElevatedButton(
                      onPressed: () { 
                        viewModel.pickAudioFile(context);
                      },
                      child: const Text('Upload File'),
                    ),
                    const SizedBox(
                      height: 25,
                    ),
                    Text(
                      'File: ${viewModel.pickedFileName ?? "No file selected"}'
                    ),
                    const SizedBox(
                      height: 50,
                    ),
                    Text(recordingTitleText),
                    TextField(
                      controller: viewModel.titleController,
                      decoration: InputDecoration(
                        hintText: recordingTitleHint,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(
                      height: 25,
                    ),
                    Text(recordingDescriptionText),
                    TextField(
                      controller: viewModel.descriptionController,
                      decoration: InputDecoration(
                        hintText: recordingDescriptionHint,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(
                      height: 25,
                    ),
                    const Text('If the recording has separate parts, add the first words of each part:'),
                    const SizedBox(
                      height: 5,
                    ),
                    DynamicForm(
                      onControllersChanged: (controllers) => viewModel.updateControllers(controllers),
                      ),
                    const SizedBox(
                      height: 25,
                    ),
                    Text(emailText),
                    TextField(
                      controller: viewModel.emailController,
                      decoration: InputDecoration(
                        hintText: emailHint,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(
                      height: 25,
                    ),
                    Text(nameText),
                    TextField(
                      controller: viewModel.nameController,
                      decoration: InputDecoration(
                        hintText: nameHint,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(
                      height: 25,
                    ),
                    IgnorePointer(
                      ignoring: viewModel.isContextSet == false,
                      child: MaterialButton(
                        onPressed:() {
                          viewModel.runSummarization(dynamicFormKey.currentContext);
                        },
                        color: kcDarkGreyColor,
                        child: const Text(
                          'Summarize!',
                          style: TextStyle(
                            color: Colors.white
                          ),
                        ),
                      ),
                    )
                  ],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    MaterialButton(
                      color: kcDarkGreyColor,
                      child: const Text(
                        'Get in Contact',
                        style: TextStyle(
                          color: Colors.white,
                        ),
                      ),
                      onPressed: viewModel.showDialog,
                    ),
                    MaterialButton(
                      color: kcDarkGreyColor,
                      child: const Text(
                        'Show Controls',
                        style: TextStyle(
                          color: Colors.white,
                        ),
                      ),
                      onPressed: viewModel.showBottomSheet,
                    ),
                  ],
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}
