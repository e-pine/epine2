// stock script
  var currentYearIndex = 0;
  // var grandTotals = [
  //     {% for year, totals in totals_by_year.items %}
  //         {{ totals.grand_total }},
  //     {% endfor %}
  // ];

  var totalExpenses = [
      {% for entry in total_expense_yearly %}
          {{ entry.total }},
      {% endfor %}
  ];
  var overallData = [
      {% for year, value in overall.items %}
          {{ value }},
      {% endfor %}
  ];

  var initialPieChartData = getYearlyPieChartData(0);

  var yearlyPieChartCanvas = document.getElementById('yearlyPieChart').getContext('2d');
  var yearlyPieChart = new Chart(yearlyPieChartCanvas, {
      type: 'pie',
      data: initialPieChartData,
      options: {
          responsive: true,
          plugins: {
              tooltip: {
                  callbacks: {
                      label: function(context) {
                          return context.label + ': ' + context.parsed.toFixed(0) + '%'; // Add '%' to tooltip labels
                      }
                  }
              }
          }
      }
  });

  function getYearlyPieChartData(yearIndex) {
      var overall = (overallData[yearIndex] / (overallData[yearIndex] + totalExpenses[yearIndex])) * 100;
      var totalExpensePercentage = 100 - overall;

      var yearlyPieChartData = {
          labels: ['Profit', 'Invested'],
          datasets: [
              {
                  data: [overall, totalExpensePercentage],
                  backgroundColor: [
                      'rgba(255, 99, 132, 0.6)',
                      'rgba(54, 162, 235, 0.6)',
                  ],
                  borderColor: [
                      'rgba(255, 99, 132, 1)',
                      'rgba(54, 162, 235, 1)',
                  ],
                  borderWidth: 1
              }
          ]
      };

      return yearlyPieChartData;
  }

  function nextYear() {
      currentYearIndex = (currentYearIndex + 1) % roiYears.length;

      var newPieChartData = getYearlyPieChartData(currentYearIndex);
      yearlyPieChart.data = newPieChartData;
      yearlyPieChart.update();

      document.getElementById('currentYearLabel').innerText = 'Year: ' + roiYears[currentYearIndex];

      updateYearlyDataTable(currentYearIndex);
  }

  function updateYearlyDataTable(yearIndex) {
      var tableBody = document.getElementById('yearlyDataBody');
      tableBody.innerHTML = '';

      var categories = ['Returned(₱)', 'Invested(₱)', 'Profit(₱)', 'ROI(%)'];
      var amounts = [grandTotals[yearIndex], totalExpenses[yearIndex], overallData[yearIndex], roiValues[yearIndex]];

      for (var i = 0; i < categories.length; i++) {
          var newRow = tableBody.insertRow();
          var cell1 = newRow.insertCell(0);
          var cell2 = newRow.insertCell(1);

          cell1.textContent = categories[i];
          cell2.textContent = amounts[i].toLocaleString();
      }
  }

//   endstock script__________________________________________________________________________________________________

// FOR SALES TREND----------------------------------------------------------------------------------------------------

