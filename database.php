<head>



<style>

table

{

border-style:solid;

border-width:2px;

border-color:pink;

}

</style>

</head>

<body bgcolor= "#EEFDEF">

<?php


$servername = "localhost";
$username = "root";
$password = "root";
$dbname = "Project_0";
// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
 die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT * FROM kg";
$result = $conn->query($sql);



echo "<table border='1'>

<tr>

<th>Device_id</th>

<th>device_type</th>

<th>measurement</th>

<th>timestamp</th>

</tr>";

 

//while($row = mysql_fetch_array($result))
 while($row = $result->fetch_assoc()) {

  

 echo "<tr>";

  echo "<td>" . $row['one'] . "</td>";

  echo "<td>" . $row['two'] . "</td>";

  echo "<td>" . $row['three'] . "</td>";

  echo "<td>" . $row['four'] . "</td>";

  echo "</tr>";
  


  }

echo "</table>";

 

$conn->close();
?>
