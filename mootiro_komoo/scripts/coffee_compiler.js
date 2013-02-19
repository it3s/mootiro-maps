#! /usr/bin/env node

var fs         = require('fs'),
    walk       = require('walk'),
    argv       = require('optimist').argv,
    exec       = require('child_process').exec,
    fs_watcher = require('./fs_watcher');

var baseDir = ['static/js', 'static/tests'];


var formatedDate = function(date){
  return '' + date.getHours() + ':' + date.getMinutes() +
         ':' + date.getSeconds();
};

var compileCoffee = function(filepath) {
    fs.readFile(filepath, function(err, data) {
      if(err) {
        throw err;
      }
      var lines, flag, cmd, now;

      lines = data.toString().split("\n");

      flag = (lines[0].indexOf('no-wrap') > -1) ? '-b' : '';

      cmd = 'coffee ' + flag + ' -c ' + filepath;
      now = new Date();

      console.log('[coffee] ' + formatedDate(now) + ' : ' + filepath);
      exec(cmd, function(error, stdout, stderr){
          if (stdout) {
            console.log(stdout);
          }
          if (error !== null) {
            console.log('error:: ' + error);
          }
      });
    });
};

var compileAll = function() {
  var walker, dir, i;
  for (i=0; i<baseDir.length; i++) {
    dir = baseDir[i];
    walker = walk.walk(dir, {followLinks: false});
    walker.on("file", function (root, fileStats, next) {
      filepath = root + '/' + fileStats.name;
      if (fileStats.name.match(/.*\.coffee$/)){
        compileCoffee(filepath);
      }
      next();
    });
  }
};

// compile all or watch
if (argv.all){
  compileAll();
} else {
  var dir, i;
  for (i=0; i<baseDir.length; i++) {
    dir = baseDir[i];
    fs_watcher.watch(dir, /.*\.coffee$/, function (path, curr, prev) {
      compileCoffee(path);
    });
  }
}

