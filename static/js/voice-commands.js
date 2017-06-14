$(document).ready(function() {
  "use strict";

  if (annyang) {
    // Define the functions our commands will run.
    var hello = function() {
      var msg = new SpeechSynthesisUtterance('Hello user. WHat I can do for you?');
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(msg);
    };
    var goto = function(page) {
      var selector = 'a[data-annyang="' + page + '"]';
      var matches = $(selector);

      if (matches.length === 1) {
        matches.trigger('click');
      }
      else {
        var msg = new SpeechSynthesisUtterance("Sorry, I don't understand you");
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
      }
    };
    var add_item = function(item) {
      var selector = 'button[data-annyang="add ' + item + '"]';
      var matches = $(selector);

      if (matches.length === 1) {
        matches.trigger('click');
      }
      else {
        var msg = new SpeechSynthesisUtterance("Sorry, I don't understand you");
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
      }
    };
    var close_modal = function() {
      $('.modal.in').modal('hide');
    };
    var annyang_stop = function() {
      annyang.abort();
      var msg = new SpeechSynthesisUtterance('Goodbye!');
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(msg);
    };
    // define our commands.
    // * The key is the phrase you want your users to say.
    // * The value is the action to do.
    //   You can pass a function, a function name (as a string), or write your function as part of the commands object.
    var commands = {
      'hello (there)':        hello,
      'go to *page':          goto,
      'add *item':            add_item,
      'clean':                close_modal,
      'stop':                 annyang_stop,
//      'show :type report':    showTPS,
//      'let\'s get started':   getStarted,
    };
    // OPTIONAL: activate debug mode for detailed logging in the console
    annyang.debug();
    // Add voice commands to respond to
    annyang.addCommands(commands);
    // OPTIONAL: Set a language for speech recognition (defaults to English)
    // For a full list of language codes, see the documentation:
    // https://github.com/TalAter/annyang/blob/master/docs/FAQ.md#what-languages-are-supported
    annyang.setLanguage('en');
    // Start listening. You can call this here, or attach this call to an event, button, etc.
    annyang.start();
  }
});
