model = {
		"source": """<h1>Add a Page</h1>
<div>
    <form id='form'>
        <input placeholder="Page name here" id="name"/>	
        <br/>
        <input id='create' type='submit' value='Create'/>
    </form>
</div>
""",
		"css": """#name {    
    font-size: 1.1em;    
    text-align: center;    
    border: none;   
    border-bottom: 2px solid black;    
    background-color: #eee;
    padding: 10px;
    outline: none;
    width: 300px;
}
#create {    
    appearance: none;    
    padding: 10px;    
    font-weight: bold;    
    color: white;    
    background-color: black;    
    font-size: 1.1em;
    border: none;
    margin-top: 0.5em;
}""",
		"js": """
		$("#form").submit(function() {
		    var name = $("#name").val();
		    name = name.replace(/ /g, '-');
		    window.location = '/' + encodeURI(name) + "?edit";
		    return false;
		});
		
		""",
		"title": "New Page"
	}
