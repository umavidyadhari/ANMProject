#!/usr/bin/perl

#ANM Project Switch Monitor
# Author: Jorge Alberto Medina
# BTH: Karlskrona, SWEDEN

use strict;
use warnings;
use Net::SNMP;
use DBI;
use List::MoreUtils;

my $logdate=localtime();
print "LogDate: $logdate\n\n";

#DataBase Parameters:
my $driver = "mysql"; 
my $database = "anmdb";
my $dsn = "DBI:$driver:database=$database";
my $user = "root";
my $password = "admin123";
my $dbh = DBI->connect($dsn, $user, $password ) or die $DBI::errstr;
print "DEBUG: The connection to the DB is OK..\n";

#Array holders for values to be inserted in the inventory table
my(@mac,@port,@status,$hostname,@names1);
my ($x,$counter);

#MIB-2 Declaration MAC-PORT-STATUS
my $macMib2='.1.3.6.1.2.1.17.4.3.1.1';
my $portMib2='.1.3.6.1.2.1.17.4.3.1.2';
my $statusMib2='.1.3.6.1.2.1.17.4.3.1.3';

#Array Declaration: @names: contains the oid from get_next_request
#@names1: contains the root OIDs
my @names=@names1=($macMib2,$portMib2,$statusMib2);


#1. We have to query the DB to see if there is any device to probe
my $q1=qq(select count(*) from credentials;);
my $q1h = $dbh->prepare($q1);
my $q1r = $q1h->execute() or die $DBI::errstr;
if($q1r < 0) {
   	print $DBI::errstr;
   	exit(1);
}
my $output=$q1h->fetchrow_array();

#If devices, then we proceed to probe the devices
if ($output){
	my ($snmp_session, $snmp_error);
	#We have to proceed to probe the devices
	
	#1. We need to go to the DB to get the credential(IP/Community)
	$q1=qq(select devip,devcommunity,devname,devtype from credentials;);
	$q1h = $dbh->prepare($q1);
	my $q1r = $q1h->execute() or die $DBI::errstr;
	if($q1r < 0) {
   		print $DBI::errstr;
   		exit(1);
    }
    ################################################################
    while(my @row=$q1h->fetchrow_array()){
    	#we have to create connections per entry
    	($snmp_session, $snmp_error)=Net::SNMP->session(
    				-hostname => $row[0],
    				-community => $row[1],
    				-timeout   =>3,
    				-retries   =>0,
    				);
    	if (!defined($snmp_session)){
    		print "ERROR: $snmp_error ";
    		exit(1);
    	}
    	$hostname=$row[2];
    	print "DEBUG: the session with IP: $row[0] and community:$row[1]\n";
		
		############What type of device is it? ######################
		my $sysDes = $snmp_session->get_request(
                          -varbindlist      =>['1.3.6.1.2.1.1.1.0'],
                      );
		
		#if nothing is coming
		if(!$sysDes){
			print "The device does not respond to SNMP Requests...\n";
			$snmp_session->close();
			next;
		}
		my $device_vendor=$sysDes->{'1.3.6.1.2.1.1.1.0'};
		##############################################################
	
	#if the device is a switch then we start processing	
		if($row[3]=~/SW/){
			$counter=0;
			#We start looping get_next_request until we have navigate over the MIB
		
############################PROCESSING CODE###########################################
			while(1){
				# the first get_next_request will be using @names from table MIB
				my $result = $snmp_session->get_next_request(
                	          -varbindlist      =>\@names,
                    	   );
			
				#We start getting the information from get_next_response
			
				#@names contains the OID from the snmp_get_next
				@names=$snmp_session->var_bind_names();
			
				#The SNMP device does not respond.
				unless(scalar @names){
					print "DEBUG: The device did not respond to the SNMP request\n";
					last;
				}
		
				#$resultoid contains the reference to the actual values
				my $resultoid= $snmp_session->var_bind_list();
				#We start looping over the OIDs obtained....
				foreach (@names){
					my $oid_result=$resultoid->{$_};
					#print "I am here $oid_result\n";
				
					if ($_=~/$names1[0]/){
						#print "The OID is: $_ and the value is: $oid_result\n";
						#$oid_result=~ tr/[`',]/ /;
						#$oid_result=~ s/\s//g;
						push(@mac,$oid_result);
						next;
					}
					elsif($_=~/$names1[1]/){
						push(@port,$oid_result);
						next;
					}
					elsif($_=~/$names1[2]/){
						#(status:1-other, 2-invalid, 3-learned, 4-self, 5-mgmt
						push(@status,$oid_result);
						next;
					}						
	
					#Here we have to place elsif for other cases		
		
		
					#If the Objects OIDs exceed the MIB we are interested in
					if(scalar @mac && scalar @port && scalar @status){
						#We proceed to insert into the database
			
						######DATABASE CODE TO HANDLE ENTRIES ########
						my $qx=qq(select count(*) from inventory where devname='$hostname';);
						my $qxh = $dbh->prepare($qx);
						my $qxr = $qxh->execute() or die $DBI::errstr;
						my $output=$qxh->fetchrow_array();
					
						#If there is any row in the table
						if ($output){
							#print "Wll Medina\n";
							#print "Geo".scalar @mac."\n";
							my @macmatch;
							my $qy=qq(select mac from inventory where devname='$hostname';);
				    		my $qyh = $dbh->prepare($qy);

						
							for(my $i=0;$i<scalar @mac;$i++){
								my $qyr = $qyh->execute() or die $DBI::errstr;
								while(my @ry=$qyh->fetchrow_array()){
									if($mac[$i] eq $ry[0]){
										#We have to update the entry
										my $qi=qq(update inventory set status=$status[$i],port=$port[$i],
    			                       		modif_date=now() where mac="$mac[$i]";);
    				            		my $rv = $dbh->do($qi) or die $DBI::errstr;	
										#print "hehehe $i\n";
										push(@macmatch,$mac[$i]);
								
									}#FIN if statement
								
								}#FIN for while loop for entries coming from probing
						
							}#FIN for loop for entries coming from probe


							#We find the MACs that are not in the table, and proceed to insert them
							#into the table.
							#######################################################################################
							foreach my $f (@mac){
								if($f=~/0x/){
									unless ( grep( /^${f}$/, @macmatch) ) {
										my $i=List::MoreUtils::first_index {$_ eq $f} @mac;
										my $qi=qq(INSERT INTO inventory (creation_date,devname,mac,port,status)
												values (now(),'$hostname',"$mac[$i]",$port[$i],$status[$i]););
										my $rv = $dbh->do($qi) or die $DBI::errstr;
										#print "DEBUG: MAC new to be inserted..\n";
									}								
								}
							}
						
							#######################################################################################
						
							###############################################################################
							#This block of code is going to delete the information in the table 
							#That is not in the table.
							my $qyr = $qyh->execute() or die $DBI::errstr;
								while(my @ry=$qyh->fetchrow_array()){
									if($ry[0]=~/0x/){
										unless(grep( /^${ry[0]}$/, @mac)){
											my $qi=qq(DELETE FROM inventory where mac="$ry[0]";);
											my $rv = $dbh->do($qi) or die $DBI::errstr;
											#print "DEBUG: one entry was deleted..\n";
										}
									}
									else{
										my $qi=qq(DELETE FROM inventory where mac="$ry[0]";);
										my $rv = $dbh->do($qi) or die $DBI::errstr;
										#print "DEBUG: one weird entry was deleted..\n";
									}
								}
							############################################################################	



						}#If for in case the table is not empty
						else{
							#print "DEBUG:table not empty".scalar @mac."\n";
					
							for(my $i=0;$i<scalar @mac;$i++){
								my $q1=qq(INSERT INTO inventory (creation_date,devname,mac,port,status)
     						    	values (now(),'$hostname',"$mac[$i]",$port[$i],$status[$i]););
    				    		my $rv = $dbh->do($q1) or die $DBI::errstr;
							}
						}#FIN ELSE CLASE

						print "DEBUG: the probe for device: $hostname is done...\n";
						#We flush the contructor buffers
						undef @mac;
						undef @port;
						undef @status;
					}#fin elseif
				
					else{
						print "No response to standard MIBs\n";
						my $qy=qq(select vendor,macoid,portoid,statusoid from enterpriseoid;);
				    	my $qyh = $dbh->prepare($qy);
				    	my $qyr = $qyh->execute() or die $DBI::errstr;
				    	my ($macEnt,$portEnt,$statusEnt);
						while(my @ry=$qyh->fetchrow_array()){
							if($device_vendor=~/$ry[0]/){
								$macEnt=$ry[1];
								$portEnt=$ry[2];
								$statusEnt=$ry[3];
								print "The device is: $ry[0]..\n";
								last;
							}		
						}
						if(!defined $macEnt or !defined $portEnt or !defined $statusEnt){
							print "No standard MIB Found :(\n";
							last;
						}
						print "$hostname: does not respond to standard MIBs\n";
						print "EnterpriseOIDs:\n";
						print "++++++++++++++++\n";
						print "MAC oid=$macEnt\n";
						print "Port oid=$portEnt\n";
						print "Status oid=$statusEnt\n";
						#This loops for the next device
						last;				
					}	
			}
######################END PROCCESSING BLOCK######################################################
		
			#This block will check if the counters have been surpassed.
        	for($x=0;$x<scalar @names;$x++){
            		unless($names[$x]=~/${names1[$x]}/){
            			$counter++;
            		}            	            	
        	}
        	if($counter==scalar @names){
        		#print ">>>>>\n";
            	last;
        	}
               
			}#FIN while loop with Get_next_request			
			#We reset the value of the OID for the next device to be the standard
		
			$snmp_session->close();
			@names=@names1=($macMib2,$portMib2,$statusMib2);;
			#print join(":",@names)."\n";
			print "************************************\n";
  	}#FIN in the case of the device is a Switch
  	
  	else{
  		#This will be the part of the code that will check the routers
  		
  		#Standard MIB declaration for the IP interfaces:
  		my $ipoid='1.3.6.1.2.1.4.20.1.1';
  		my $ipindexoid='1.3.6.1.2.1.4.20.1.2';
  		my @routeroid=($ipoid,$ipindexoid);
  		my @routeroid1=($ipoid,$ipindexoid);
  		#We then start probing the device:
  		my (@ip,@ipindex,@ipname);
  		my $counter1=0;
  		
  		while(1){
  			
  			my $result = $snmp_session->get_next_request(
                	          -varbindlist =>\@routeroid,
                    	   );
                    	   
            #@names contains the OID from the snmp_get_next
			@routeroid=$snmp_session->var_bind_names();
			#print "DEBUG: ".join("+",@routeroid)."\n";
			#The SNMP device does not respond.
			unless(scalar @routeroid){
				print "DEBUG: The device did not respond to the SNMP request\n";
				last;
				}
			my $resultoid= $snmp_session->var_bind_list();
			foreach (@routeroid){
				#$resultoid contains the reference to the actual values
				
				my $oid_result=$resultoid->{$_};	
				if($_=~/$ipoid/){
					#print "I am here...\n";
					push(@ip,$oid_result);
				}
				elsif ($_=~/$ipindexoid/){
					#print "I am there...\n";
					push(@ipindex,$oid_result);
				}
				
			}#FIN for foreach
			
			#This block will check if the counters have been surpassed.
        	for(my $v=0;$v<scalar @routeroid;$v++){
            		unless($routeroid[$v]=~/${routeroid1[$v]}/){
            			$counter1++;
            		}            	            	
        	}
        	if($counter1==scalar @routeroid){
        		#print ">>>>>\n";
            	last;
        	}
        	if(scalar @ip and scalar @ipindex){
        		
  				my $resultx = $snmp_session->get_request(
                	          -varbindlist =>['1.3.6.1.2.1.31.1.1.1.1.'.$ipindex[0]],
                    	   );
                    	                 
  				my $int_name=$resultx->{'1.3.6.1.2.1.31.1.1.1.1.'.$ipindex[0]};
  				my $sth2=$dbh->do("insert into router (creation_date,devname,ip,ifname,modif_date) values (now(),'$hostname','$ip[0]','$int_name',NULL)
  				on duplicate key update modif_date=now()");
  				
  				print "The information was successfully inserted\n";
  				undef @ipindex;
  				undef @ip;
  			}
  			else{
  				print "DEBUG: The router does not respond to standard MIB...\n";
  				last;
  			}

  		}#FIN of while loop
  		
  		}#FIN else in case of R
  			    	
    }#FIN While loop of Devices
		
}#FIN IF DEVICES TO DISCONNECT


else{
	print "DEBUG: No device to probe..\n";
	#$dbh->disconnect;
	exit(0);
}



