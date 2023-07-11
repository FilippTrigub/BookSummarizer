/// The max width the content can ever take up on the screen
const double kdDesktopMaxContentWidth = 1150;

// The max height the homeview will take up
const double kdDesktopMaxContentHeight = 750;

// Backend URI and port
const backendUri = String.fromEnvironment('API_URI', defaultValue: 'localhost');
const String backendEndpoint = 'http://$backendUri';
