
<!-- Here is an simple login site for the database interface, which is also the first page for user. In this page, users can login with an username and password to access the database. If the user provides the wrong username or password, they are not alowed to enter the database.-->

<style>
  /* The css code for the font is below*/
.u-section-1 .u-text-1 {
  font-size: 3.75rem;
  width: 514px;
  margin: 75px auto 0;
}

@media (max-width: 767px) {
  .u-section-1 .u-text-1 {
    font-size: 2.8125rem;
    margin-top: 70px;
  }
}

@media (max-width: 575px) {
  .u-section-1 .u-text-1 {
    font-size: 2.25rem;
    width: 340px;
    margin-top: 60px;
  }
}

/* The login page consists of an login frame on an empty background.
On the frame, there are 2 labels for input, and a button to login.*/
	body{   
    background: white;  
}  

/* Here is the style for the login frame*/
#frm{  
    border: solid gray 1px;  
    width:25%;  
    border-radius: 2px;  
    margin: 120px auto;  
    background: #1abc9c;  
    padding: 50px;  
}  
#btn{  
    color: #fff;  
    background: black;  
    padding: 7px;  
    margin-left: 70%;  
}  
</style>

<html>  
<head>  
    <title>PHP login system</title>    
</head>  
<body>  
    <div id = "frm">  
        <h2 class="u-text utext-1">Kitchen Guard Database</h2> 
        <form name="f1" action = "database.php" onsubmit = "return validation()" method = "POST">  
          <!-- If the function below(the validation funtion) return true, the page will jump to database.php, which means you have secssesfuly loged in to the database.-->

          <!--the html code below crate the login frame and locate where the labels and the button should be.-->
            <p>  
                <label> UserName: </label>  
                <input type = "text" id ="user" name  = "user" />  
            </p>  

            <p>  
                <label> Password: </label>  
                <input type = "password" id ="pass" name  = "pass" />  
            </p>  

            <p>     
                <input type =  "submit" id = "btn" value = "Login" />  
            </p>  

            <p>  
                <label> Try to login with any username and password </label  
            </p>  

        </form>  
    </div>  
      
    <script>  
            function validation()  
            {  

              /*This JavaScript function make sure that, users have to provide a valid username and password, if not, they are notified by some pop up messages that saying you are missing information(and simply tells your what the username and password are.) */
                var id=document.f1.user.value;  
                var ps=document.f1.pass.value;  
                if(id.length=="" && ps.length=="") {  
                    alert("User Name and Password fields are empty");  
                    return false;  
                }  
                else if (id.length=="")  
                {  
                    alert("User Name is empty");  
                        return false;  
                }   
                else  if (ps.length=="") 
                {  
                    alert("Password field is empty");  
                    return false;  
                }  
                 else
                {
                	if (id != 'root'){
                		alert("User name and password are: root")
                		return false;
                	}
                	if (ps != 'root'){
                		alert("User name and password are: root")
                		return false;
                	}
                }  
            }  
        </script>  
</body>     
</html>  
