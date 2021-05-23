<head> 
  <!-- This .php file is a simple visualization of the main Kitchengaurd database interface. The page includes a header and a "real-time" table to print out the data from the database. 
  Since this is just a simple page, the css, html, and the php code for database is in the same file.-->

<style>
table /*Here is the css style for the table that the data appears in*/
{     
  /* The code below controls the location of where the table should be in the webpage(central), the border style, width and color*/
border-style:solid;
margin-left: auto;
margin-right: auto;
border-width:2px;
border-color:pink;

}

.header {
  /*The header style is decided under this part, where the font-size, background color of the header and the text location is been considered here. */
  padding: 3px;
  text-align: left;
  background: #1abc9c;
  color: white;
  font-size: 15px;
}

</style>
</head>
<!--A littel bit html code is here. -->
<body bgcolor= white>
<div class="header">
  <h1>Kitchen Guard Database </h1>
  <a href onClick="window.location.reload();">Update database</a>
  <a href="/index.php">Log out</a>
  <!-- There are two buttons in the header where one is refreash and the other is logout-->
</div>

<?php
// php code for create connection to database starts here.
$servername = "localhost";
$username = "root";
$password = "root";
$dbname = "kg_data";
// declare the information that you need to log in to the database. Then use the information to connect to the database.
$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
 die("Connection failed: " . $conn->connect_error);
 // Ckeck the connection here, if there are some error, then print it out.
}

// After connected to the database with the correct information, the table from the database named"kg_table" has been chosen and the contents is saved to the variable called "result".
$sql = "SELECT * FROM kg_table";
$result = $conn->query($sql);


echo "<table border='1'>
<tr>
<th>Timestamp:</th>
<th>Value:</th>
<th>Event type:</th>
<th>Event type enum: </th>
<th>Device model: </th>
<th>Device vendor: </th>
</tr>";
// The first row of the table is been hardcoded to be the title of the contents for each column.
// After that, the contents from the table in database will be automatically fetched in by the while loop.

  while($row = $result->fetch_assoc()) {
    echo "<tr>";
    echo "<td>" . $row['timestamp'] . "</td>";
    echo "<td>" . $row['value'] . "</td>";
    echo "<td>" . $row['event_type'] . "</td>";
    echo "<td>" . $row['event_type_enum'] . "</td>";
    echo "<td>" . $row['device_model'] . "</td>";
    echo "<td>" . $row['device_vendor'] . "</td>";
    echo "</tr>";
  }
echo "</table>";

$conn->close();
/*at the end, close the connection to the database.*/
?>