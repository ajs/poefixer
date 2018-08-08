#!/usr/bin/env perl
#

use HTML::Entities qw(decode_entities);
use LWP::Simple qw(get);

use v5.20.0;
use strict;

my $page = get('http://currency.poe.trade/tags');
my $a = 0; # Alternation between name and abbrev
my $name;
for my $line (split /\r?\n/, $page) {
    if ($line =~ /\<td\b[^\>]*\>\s*(.*?)\s*\<\/td\b[^\>]*\>/) {
        if (++$a % 2 == 0) {
            say qq{"}.decode_entities($_).qq{": "$name",} for (split /\s*,\s*/, $1);
        } else {
            ($name = decode_entities($1)) =~ s/\<img\b[^\>]*\>\s*//
        }
    }
}
