$(document).ready(function() {
  "use strict";

  if (annyang) {
    // Define the functions our commands will run.
    var hello = function() {
      var msg = new SpeechSynthesisUtterance('Hello user. WHat can I do for you?');
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
    var save_modal = function() {
      $('.modal.in').find('button[type="submit"]').trigger('click');
    };
    var cancel_modal = function() {
      $('.modal.in').modal('hide');
    };
    var annyang_events = function() {
      var text = 'No events for today';
      var msg;

      $.getJSON('events', function(events) {
        if (events) {
          text = events;
        }
        msg = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
      });
    };
    var annyang_time = function() {
      var currentdate = new Date();
      var msg = currentdate.getHours() + ' hours and ' + currentdate.getMinutes() + ' minutes';

      msg = new SpeechSynthesisUtterance(msg);
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(msg);
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
      'save':                 save_modal,
      'cancel':               cancel_modal,
      'today\'s events':      annyang_events,
      'what time is it':      annyang_time,
//      'play me something':    annyang_paly,
      'goodbye':              annyang_stop,
    };
    // OPTIONAL: activate debug mode for detailed logging in the console
    annyang.debug();
    // Add voice commands to respond to
    annyang.addCommands(commands);
    // OPTIONAL: Set a language for speech recognition (defaults to English)
    // For a full list of language codes, see the documentation:
    // https://github.com/TalAter/annyang/blob/master/docs/FAQ.md#what-languages-are-supported
    annyang.setLanguage('en');
    // Tell KITT to use annyang
    SpeechKITT.annyang();

    // Render KITT's interface
    SpeechKITT.vroom();
  }
});
