function gotEmployees(data) {
    console.log(data);
    $("#userdetails")[0].innerHTML=`<h1 id="Details"> Details for ${data.fname}  ${data.lname}</h1>
    <h2 id="Details"> ${data.title} </h2>
    <table>
      <tr>
        <th id="Details"> First name: </th>
        <td id="Details"> ${data.fname}</td>
      </tr>
      <tr>
        <th id="Details"> Last name: </th>
        <td id="Details"> ${data.lname}</td>
      </tr>
      <tr>
        <th id="Details"> Email: </th>
        <td id="Details"> ${data.email}</td>
      </tr>

      <tr>
        <th id="Details"> Phone: </th>
        <td id="Details"> ${data.phone}</td>
      </tr>
    </table>
    <br>
    <h3 id="Details"> Leave Details </h3>
    <table>
      <tr>
        <th id="Details"> Total Leaves:   </th>
        <td id="Details"> ${data.total_leaves}</td>
      </tr>
      <tr>
        <th id="Details"> Leaves Taken:  </th>
        <td id="Details"> ${data.leaves_taken}</td>
      </tr>
      <tr>
        <th id="Details"> Leaves Remaining: </th>
        <td id="Details"> ${data.leaves_remaining}</td>
      </tr>
    </br>
    </table>
    <br>
    <h3 id="Details"> Add leave: </h3>
    <br>
    <form action="/employees/${data.id}" method=post class="row g-3 needs-validation" novalidate >
        <div class="col-md-4">
          <label id="Details" for="validationCustom01" class="form-label">Date: </label>
          <div id="form" class="input-group has-validation">
          <input type=date class="form-control" id="validationCustom01" name="Date" required>
          
        </div>
        </div>
        <div class="col-md-4">
          <label id="Details" for="validationCustom02" class="form-label">Reason: </label>
          <div id="form"  class="input-group has-validation">
          <input type="text" class="form-control" id="validationCustom02" value="Laziness" name="Reason" required>
        </div>
        </div>
       <div style="padding-left: 90px;" class="col-12">
          <button class="btn btn-outline-light" type=submit>Submit Leave</button>
        </div>
      </form>
    </br>
  </br>
    </br>
  </div>
`}

$(function() {
    $("a.userlink").one("click", function (ev) {
        $.get(ev.target.href, gotEmployees);
        ev.preventDefault();
        $(this).click(function () { return false; });
        });
});
