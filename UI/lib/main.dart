import 'package:flutter/material.dart';
import 'package:responsive_builder/responsive_builder.dart';
import 'package:test_stacked_web_app/app/app.bottomsheets.dart';
import 'package:test_stacked_web_app/app/app.dialogs.dart';
import 'package:test_stacked_web_app/app/app.locator.dart';
import 'package:test_stacked_web_app/app/app.router.dart';
import 'package:test_stacked_web_app/ui/common/app_colors.dart';
import 'package:url_strategy/url_strategy.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:logging/logging.dart';

void main() {
  Logger.root.level = Level.ALL; // defaults to Level.INFO

  Logger.root.onRecord.listen((record) {
    print('${record.level.name}: ${record.time}: ${record.message}');
  });

  var logger = Logger('MyLogger');
  
  setPathUrlStrategy();
  setupLocator(
    stackedRouter: stackedRouter,
  );
  setupDialogUi();
  setupBottomSheetUi();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ResponsiveApp(
        builder: (_) => MaterialApp.router(
              title: 'Audio Summarizer',
              theme: Theme.of(context).copyWith(
                primaryColor: kcBackgroundColor,
                focusColor: kcPrimaryColor,
                textTheme: Theme.of(context).textTheme.apply(
                      bodyColor: Colors.black,
                    ),
              ),
              routerDelegate: stackedRouter.delegate(),
              routeInformationParser: stackedRouter.defaultRouteParser(),
            ).animate().fadeIn(
                  delay: const Duration(milliseconds: 50),
                  duration: const Duration(milliseconds: 400),
                ));
  }
}
