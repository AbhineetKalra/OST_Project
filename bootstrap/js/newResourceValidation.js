function validateForm() {
		var x = document.getElementById("startTime").value;
		var temp=true;
		var y = document.getElementById("endTime").value;
		if (x>y)
			{
			alert(" Availability end time cant be less than start time");
			temp=false;
			return false;
			}
		if(temp){
			alert(" Success! Resource Created! ");
		}
}