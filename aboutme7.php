<!DOCTYPE html>
<html lang="zh-TW">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>洪詩晴的簡介</title>

	<style type="text/css">
		* { font-family:"標楷體"; margin-left:auto; margin-right:auto;}
		h1 {color:pink; font-size:60px;}
		h2 {color:#33ff33; font-size:40px;}
	</style>
	<script>
		function change1() {
  			document.getElementById("pic").src = "mountain.jpg";
  			document.getElementById("h2text").innerText = "靜宜資管";
		}

		function change2() {
  			document.getElementById("pic").src = "cliff.jpg";
  			document.getElementById("h2text").innerText = "Tzyy-Ching Yang";
		}
	</script>
</head>
<body>
	<?php echo date("Y-m-d") ?>
	<table width="70%">
		<tr>
			<td>
				<img src="cliff.jpg" width="100%"id="pic" onmouseover="change1()" onmouseout="change2()"></img>
			</td>

			<td>
				<h1>洪詩晴</h1>
				<h2 id="h2text">SHIH-CHING HONG</h2>
			</td>
		</tr>
	</table>
		<table width="70%" border="1">
		<tr>
			<td>
				個人網頁：<a href="https://www1.pu.edu.tw/~tcyang">https://www1.pu.edu.tw/~tcyang</a><br>
				FB：<a href="https://www.facebook.com/tcyang1971" target="_blank">https://www.facebook.com/tcyang1971</a><br>
				Tel: <a href="tel:0426328001,18110">04-26328001#18110</a><br>
				E-Mail: <a href="qinghong179@gmail.com">qinghong179@gmail.com</a><br>
			</td>

			<td>
				大象席地而坐電影配樂<br>
				<audio controls>
					<source src="elephant.mp3" type="audio/mP3">
				</audio><br>
			</td>

			<td>
				不要去臺灣<br>
				<iframe src="https://www.youtube.com/embed/pW88QFpHXa8" allowfullscreen></iframe>
			</td>
		</tr>
	</table>	

</body>
</html>