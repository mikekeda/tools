/* Needed gulp config */
var gulp = require('gulp');
var sass = require('gulp-sass');
var scsslint = require('gulp-scss-lint');
var cache = require('gulp-cached');
var autoprefixer = require('gulp-autoprefixer');
var neat = require('node-neat');
var minifycss = require('gulp-minify-css');
var concat = require('gulp-concat');
var plumber = require('gulp-plumber');
var browserSync = require('browser-sync');
var reload = browserSync.reload;
var uncss = require('gulp-uncss');
var jshint = require('gulp-jshint');
var htmlhint = require("gulp-htmlhint");
var concat = require('gulp-concat');

/* Html lint */
gulp.task('html-lint', function () {
    gulp.src('templates/*.html')
    .pipe(htmlhint())
    .pipe(htmlhint.reporter())
    .pipe(reload({stream:true}));
});

/* Js lint */
gulp.task('js-lint', function() {
  return gulp.src('static/js/main.js')
    .pipe(jshint())
    .pipe(jshint.reporter('default'));
});

/* Sass lint */
gulp.task('scss-lint', function() {
  return gulp.src('sass/style.scss')
    .pipe(cache('scsslint'))
    .pipe(scsslint());
});

/* Js task */
gulp.task('js-concat', function() {
  return gulp.src([
      'static/bower_components/jquery/dist/jquery.min.js',
      'static/bower_components/bootstrap-sass/assets/javascripts/bootstrap.min.js',
      'static/bower_components/bootstrap-html5sortable/jquery.sortable.min.js',
      'static/bower_components/moment/min/moment.min.js',
      'static/bower_components/fullcalendar/dist/fullcalendar.min.js',
      'static/bower_components/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js',
      'static/bower_components/jscolor-picker/jscolor.min.js',
      'static/bower_components/x-editable/dist/bootstrap3-editable/js/bootstrap-editable.min.js',
      'static/bower_components/annyang/dist/annyang.min.js',
      'static/bower_components/SpeechKITT/dist/speechkitt.min.js',
      'static/js/voice-commands.js',
      'static/js/main.js'
    ])
    .pipe(concat('all.js'))
    .pipe(gulp.dest('static/js'))
    .pipe(reload({stream:true}));
});

/* Sass task */
gulp.task('sass', function () {
    gulp.src('sass/style.scss')
    .pipe(plumber())
    .pipe(sass({
        includePaths: ['scss'].concat(neat)
    }))
    .pipe(uncss({
        html: ['templates/*.html', 'templates/*/*.html'],
        ignore: [
          new RegExp('.active$'),
          new RegExp('.indicators*'),
          new RegExp('.js-*'),
          new RegExp('.col-*'),
          new RegExp('.modal'),
          new RegExp('.collapsing$'),
          new RegExp('.tooltip$'),
          new RegExp('.tooltip-*'),
          new RegExp('.dropdown-menu$'),
          new RegExp('.top$'),
          new RegExp('.default$'),
          new RegExp('.bottom$'),
          new RegExp('textarea$'),
          new RegExp('.list-unstyled$'),
          new RegExp('.flipped$'),
          new RegExp('.easy .face$'),
          new RegExp('.middle .face$'),
          new RegExp('.difficult .face$'),
          new RegExp('.table-bordered$'),
          new RegExp('.fade$'),
          new RegExp('.in$'),
          new RegExp('.dataTables_wrapper'),
          new RegExp('.form-group input'),
          new RegExp('.sortable-placeholder'),
          new RegExp('.bootstrap-datetimepicker-widget'),
          new RegExp('.datepicker'),
          new RegExp('.glyphicon$'),
          new RegExp('.glyphicon-*'),
          new RegExp('.fc-event-container$'),
          new RegExp('.editable-buttons$'),
          new RegExp('@keyframes spin$'),
          new RegExp('#skitt-ui'),
          new RegExp('.editable-container$')
        ]
    }))
    .pipe(autoprefixer({
        browsers: ['last 3 versions'],
        remove: false,
        cascade: false
    }))
    .pipe(minifycss())
    .pipe(gulp.dest('static/css'))
    /* Reload the browser CSS after every change */
    .pipe(reload({stream:true}))
});

/* Prepare Browser-sync for localhost */
gulp.task('browser-sync', function() {
    browserSync.init(['static/css/*.css', 'static/js/*.js'], {
        proxy: '127.0.0.1:8000'
    });
});

/* Watch scss, js and html files, doing different things with each. */
gulp.task('default', ['scss-lint', 'sass'/*, 'browser-sync'*/], function () {
    /* Watch scss, run the sass task on change. */
    gulp.watch(['sass/*.scss', 'sass/**/*.scss', 'templates/*.html'], ['sass', 'scss-lint'])
    /* Watch app.js file, run the scripts task on change. */
    gulp.watch(['static/js/*.js'], ['js-lint', 'js-concat'])
    /* Watch .html files, run the bs-reload task on change. */
    gulp.watch(['templates/*.html'], ['html-lint']);
});
