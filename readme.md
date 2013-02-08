<h1>Usage</h1>
three documents:
<h4>(1)com.yanghua.pcMonitorService.plist</h4>
if you want to receive [pc start] msg, put the file into /Library/LaunchDaemons/.
other way,to put this file into /Library/LaunchAgents so that you can receive the msg to kown someone has logined into your system.
<h4>(2)pcMonitorService.sh</h4>
put the shell script file into /usr/local/,
and give other user execute permission in the terminal with below cmd:
<b>sudo chmod o+x /usr/local/pcMonitorService.sh</b>
<h4>(3)pcMonitor.py</h4>
it's the program logic that will be executed actually.
like pcMonitorService.sh, you should put this gay into /usr/local/.
and you should modify somewhere which I havd marked as "#TODO", mostly they are about the e-mail.

ok,now you should give the user which you want monitor more permission, such as, shutdown. yeah, shutdown! I konw it seems to be very dangerous, but you must do that, if you want it looks like fascinating！
first,modified shutdown shell
<b>sudo vi /sbin/shutdown</b>
then change the line contain:
 %users localhost=/sbin/shutdown -h now
to (remove the first sharp symbol):
%yanghua localhost=/sbin/shutdown -h now
notice:yanghua is just my pc's user name

<b>set the suid for the user of the pc that you want to monitor</b>
in the Treminal:
<b>sudo chmod u+s /sbin/shutdown</b>

<h1>Modify info</h1>
added screen shot when the network is unable and handled method:"init" exception at Fri Feb 8.

<h1>More info</h1>
more information, please go and see my blog:
<a href="http://blog.csdn.net/yanghua_kobe/article/details/8576106">http://blog.csdn.net/yanghua_kobe/article/details/8576106</a>

and if you have any problem, give me your mail:
<a href="mailto:yanghua1127@gmail.com">yanghua1127@gmail.com</a>

Have fun!