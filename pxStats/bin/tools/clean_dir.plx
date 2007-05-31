#!/usr/bin/perl
#!/opt/perl5/bin/perl
######################################################################################################
# Name: clean_dir.plx
#
# Author: Daniel Lemay
#
# Date: 2003-08-08
#
# Description: With this script, you can clean your directories recursively. In the config.
# file you enter the directories you want to clean, the pattern (glob) to match, the
# intervall of time that must be attained by a file for it to be deleted (specified in seconds (s),
# minutes (m), hours (h) or days (d) and finally it you want the delete to be recursive or not. 
# 
# WARNING: Be extremely cautious when usign this software. Be sure to understand which files will be
# selected by your pattern because when your files are gone, it's forever! Be aware that it could
# be extremely dangerous to run this program as root.
######################################################################################################
use strict;
use warnings;
use File::Spec;
use File::Find;                                            # For using finddepth

&usage;

my $CONF_FILE = shift @ARGV;                               # config file
my $LOG_FILE;                                              # log file (erase files are logged here)
my ($dir, $pattern, $time, $recursive);                    # root dir, glob for config file, time intervall, boolean
my $numb_sec;                                              # total time in seconds
my $regex;                                                 # regex obtain for the glob in config file
my $DEBUG=0;                                     

open CONFIG, $CONF_FILE or die "Cannot open $CONF_FILE: $!"; 

while (<CONFIG>) {
   if (/^LOGFILE/) {
       (my $dummy, $LOG_FILE) = split;
   }
}
close CONFIG;

open LOG, ">>$LOG_FILE" or die "Cannot open $LOG_FILE: $!"; 
open CONFIG, $CONF_FILE or die "Cannot open $CONF_FILE: $!"; 

chomp (my $date = `date`);

print LOG "BEGIN################################################################\n";
print LOG $date, " $0 has been executed\n";

while (<CONFIG>) {
   
   next if (/^#/);
   next if (/^LOGFILE/);
   ($dir, $pattern, $time, $recursive) = split;
   $numb_sec = &get_number_of_seconds(&get_time_descriptor($time)); 

   print "DEBUG: dir=$dir, pattern=$pattern, time=$time, recursive=$recursive\n" if $DEBUG; 
   print "DEBUG: Le nombre de secondes est: $numb_sec\n" if $DEBUG;

   print LOG "Directory: $dir, Pattern: $pattern, Time: $time, Recursive: $recursive\n";
   print LOG "MIDDLE***************************************************************\n";

   if ($recursive eq "yes") {
      finddepth(\&recursive_erase, $dir);
   } else {
      print "DEBUG: simple_erase is called!\n" if $DEBUG;
      simple_erase($dir); 
   }
   chomp ($date = `date`);
   print LOG $date, " $0 has terminated\n";
   print LOG "END##################################################################\n";
}
close CONFIG;
close LOG;

print "DEBUG:". glob_to_regex('list.?') . "\n" if $DEBUG;
print "DEBUG:". glob_to_regex('project.*') . "\n" if $DEBUG;
print "DEBUG:". glob_to_regex('*old') . "\n" if $DEBUG;
print "DEBUG:". glob_to_regex('type*.[ch]') . "\n" if $DEBUG;
print "DEBUG:". glob_to_regex('*.*') . "\n" if $DEBUG;
print "DEBUG:". glob_to_regex('*') . "\n" if $DEBUG;
print "DEBUG:". glob_to_regex('.pl') . "\n" if $DEBUG;

sub essai {
   
   my $dir = shift @_;
   print "La valeur de \$dir est $dir\n";
   opendir DH, $dir or die "Cannot open $dir: $!";
   foreach my $file (readdir DH) {
      print "file or dir is: $file\n";

   }

}

sub simple_erase {
   $regex = &glob_to_regex($pattern);
   print "DEBUG: ". $regex . "\n" if $DEBUG;
   my $dir = shift @_;
   opendir DH, $dir or die "Cannot open $dir: $!";
   foreach my $name (readdir DH) {
      next if $name =~ /^\.\.?$/; # Skip over . and .. directories
      my $file = File::Spec->catfile($dir, $name); # Equivalent to $dir/$file (cannot know if / is already include in $dir)
      if (-d $file) {
         print "DEBUG: directory: $file\n" if $DEBUG;
      } elsif (-f $file and $name =~/$regex/) {
         print "DEBUG: file: $file\n" if $DEBUG;
         my $now = time;
         my $past_time = $now-$numb_sec;
         if ((stat $file)[9] < $past_time) {
            print "DEBUG: On devrait effacer ce fichier!\n" if $DEBUG;
            #print LOG $date, " $file deleted\n";
            my $stat = (stat $file)[9];
            unlink $file or warn "Cannot unlink $file: $!";
         } else {
            print "DEBUG: On ne devrait pas effacer ce fichier!\n" if $DEBUG;
         }

      }
   }
   closedir DH;
}

sub recursive_erase {
   $regex = &glob_to_regex($pattern);
   print "DEBUG: ". $regex . "\n" if $DEBUG;
   if (-d $_) {
      print "DEBUG: directory: $File::Find::name\n" if $DEBUG;
   } elsif (-f $_ and /$regex/) {
      print "DEBUG: file: $File::Find::name\n" if $DEBUG;
      print "DEBUG: Dir: $File::Find::dir\n" if $DEBUG;
      print "DEBUG: \$_: $_\n" if $DEBUG;
      my $now = time;
      my $past_time = $now-$numb_sec;
      chomp(my $date = `date`); 
      if ((stat $_)[9] < $past_time){
         print "DEBUG: On devrait effacer ce fichier!\n" if $DEBUG;
         #print LOG $date, " $File::Find::name deleted\n";
         my $stat = (stat $_)[9];
         unlink $_ or warn "Cannot unlink $_: $!";
         # print "Stat for $_ is: $stat\n";
      } else {
         print "DEBUG: On ne devrait pas effacer ce fichier!\n" if $DEBUG;
         my $stat = (stat $_)[9];
         # print "Stat for $_ is: $stat\n";
      }
   }
}

sub get_time_descriptor {
      my ($number, $descriptor) = split /:/, $_[0], -1; # get quantity of time and its descriptor
      #print "Le descriptor is : $descriptor\n" if defined($descriptor);
}

sub get_number_of_seconds {
   # Conversions in seconds
   my $MINUTE = 60;
   my $HOUR = 60 * $MINUTE;
   my $DAY = 24 * $HOUR;
   
   my ($number, $descriptor) = @_;
   my $seconds;
   
   print "DEBUG: My descriptor is: $descriptor\n" if $DEBUG;

   if ($descriptor eq "s") {
      return $number;
   } elsif ($descriptor eq "m") {
      return $seconds = $number * $MINUTE;
   } elsif ($descriptor eq "h") {
      return $seconds = $number * $HOUR;
   } elsif ($descriptor eq "d") {
      return $seconds = $number * $DAY;
   } elsif ($descriptor eq "") {
      return $seconds = $number * $DAY;
   } else {
      die "Il y a un probleme avec le file descriptor dans le fichier de config!\n";
   }
}

sub glob_to_regex {
# Transform a glob into a regex
# The glob has to be not too complicated 
   my $glob = shift @_;
   my %regex_map = (
     '*' => '.*',
     '?' => '.',
     '[' => '[',
     ']' => ']',
   );
   
   $glob =~ s{(.)} {$regex_map{$1} || "\Q$1"}ge;
   return '^' . $glob . '$';
}

sub usage {
   if (scalar @ARGV != 1) {
      print "\n";
      print "Usage: clean_dir.plx configFile_fullPath\n\n";
      print "Example 1: clean_dir.plx /apps/pds/etc/clean.conf\n";
      print "\n";
      exit;
   }
}
