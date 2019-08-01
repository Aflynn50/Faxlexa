#!/usr/bin/perl -w
#*****************************************************************************#
#* $Workfile:   fms.print.01.pl  $ $Revision:   1.0  $                       *#
#* (C) COPYRIGHT METASWITCH 2019                                             *#
#*                                                                           *#
#* Send a fax through fax print using T.38 encoding.                         *#
#*                                                                           *#
#*****************************************************************************#
use strict;
use English;
use 5.006_001;
use perlregress;
use snstest;
use snsconfig;
use snssmtp;
use snssmpp;
use snslog;
use snsoutdial;

my ($lrc, $lmsg);

my $lstarttime = logtime;

#*****************************************************************************#
#* Deposit fax via SMTP                                                      *#
#*****************************************************************************#
Log("Send FAX message");

($lrc, $lmsg) = sendMessage(
  from => '13579@fax.gateway.org',
  to   => "FAX=5140001157\@metasphere.metaswitch.com",
  file => "fax.2page.fil");

if ($lrc)
{
  #***************************************************************************#
  #* Failed to send FAX                                                      *#
  #***************************************************************************#
  Log("Failed to send FAX: $lmsg");
}

#*****************************************************************************#
#* Trigger fax print through TUI                                             *#
#*****************************************************************************#
Log("Starting SIPp command");
deleteSippOutput("faxlexa_print");
my $lpid = startSippSubscriber(script => "faxlexa_print",
                               number => "5140001157");
Log("Wait for read to finish");
waitSipp($lpid);
dumpSippOutput($lpid, "faxlexa_print");

#*****************************************************************************#
#* Start a SIPp listener for the outdial                                     *#
#*****************************************************************************#
#Log("Starting SIPp outdial");
#deleteSippOutput("fax.outdial.t38");
#my $receivepid = startSippListener(script => "fax.outdial.t38");
#Log("Wait for outdial to complete");
#waitSipp($receivepid);
#dumpSippOutput($receivepid, "fax.outdial.t38");

#*****************************************************************************#
#* Check service logs                                                        *#
#*****************************************************************************#
ServiceLogParse(time => $lstarttime,
                log  => "DCL0015|DCL0034|DCL0044",
                file => "SL_UCP");

#*****************************************************************************#
#* Make a log about the test finishing.                                      *#
#*****************************************************************************#
Log("Test ENDS OK");

1;
