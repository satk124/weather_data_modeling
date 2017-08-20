app = angular.module("weather", ['ngSanitize', 'ui.select', 'chart.js']);

app.factory('transform', function(){

	var weather= {};
	var countries = {'UK':0,  'England':1, 'Scotland':2, 'Wales':3};
	weather.toModel = function(model, data){

		angular.forEach(data, function(value, metric) {
			
			angular.forEach(value, function(monthData, country){
				model[metric][countries[country]]=monthData;
			});
		  
		});
	}
	return weather;
});

app.controller('weatherCtrl',[ 
	'$scope',
	'$http',
	'transform',
	function($scope, $http, transform){

	$scope.labels = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
 $scope.series= ['UK', 'England', 'Scotland', 'Wales'];
 $scope.title_map = {'temp_min':'Minimum Temperature', 'temp_max':'Max Temperature', 'temp_mean':'Mean Temperature', 'sunshine':'Sunshine', 'rainfall':'Rainfall'}
 $scope.metrics_data = {'temp_min':[[],[],[],[]], 'temp_max':[[],[],[],[]], 'temp_mean':[[],[],[],[]], 'sunshine':[[],[],[],[]], 'rainfall':[[],[],[],[]]};
 $http.get("/getyears").then(function(response){
 	$scope.years=response.data.years;
 },
 function(){

 });
 $scope.s = {year:"2016"};

 $scope.populate_data = function(){
 	console.log("populate_data called", $scope.year);
		  $http.get("/monthwisedata/"+$scope.s.year, {}).then(function(response){
		  	console.log("data", response);
		  	transform.toModel($scope.metrics_data, response["data"]);
		  	console.log("metric_data",$scope.metrics_data)
		  }, function(err){
		  	console.log("err", err)
		  });
	}
	  $scope.populate_data();	

 
 //console.log("metric_data1", $scope.metrics_data1);

 $scope.onClick = function (points, evt) {
   console.log(points, evt);
 };


 $scope.datasetOverride = [{ yAxisID: 'y-axis-1' }, { yAxisID: 'y-axis-2' }];

$scope.colours = ["rgb(255,51,51)","rgb(51,153,255)","rgb(51,51,255)", "rgb(96,96,96)"];

 $scope.options = {
   scales: {
     yAxes: [
       {
         id: 'y-axis-1',
         type: 'linear',
         display: true,
         position: 'left'
       },
       {
         id: 'y-axis-2',
         type: 'linear',
         display: true,
         position: 'right'
       }
     ]
   }
 };

	}]);