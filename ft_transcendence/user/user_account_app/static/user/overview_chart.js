document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("mainStats")) {
    initializeCharts();
  }
});

document.body.addEventListener("htmx:load", function () {
  /* if (document.getElementById("mainStats")) {
    initializeCharts();
  } */
  requestAnimationFrame(() => {
    window.scrollTo(0, 0);
  });
});

document.body.addEventListener("htmx:afterSwap", function () {
  /* if (document.getElementById("mainStats")) {
    initializeCharts();
  } */
  requestAnimationFrame(() => {
    window.scrollTo(0, 0);
  });
});

// initialize charts for overview
function initializeCharts() {
    const gamesPie = document.getElementById("gamesPie")?.getContext("2d");
    const pointsPie = document.getElementById("pointsPie")?.getContext("2d");
    // Get the data from JSON script
    const mainStatsScript = document.getElementById("mainStats");

    if (!mainStatsScript || !gamesPie || !pointsPie) return;
    const mainStats = JSON.parse(mainStatsScript.textContent);
    if (gamesPie && pointsPie) {
      const gamesWon = mainStats.games_won;
      const gamesLost = mainStats.games_lost;
      const pointsScored = mainStats.points_scored;
      const pointsConceded = mainStats.points_conceded;
      // In case I want more data
      const gamesPlayed = mainStats.games_played;
      const winRate = mainStats.win_rate;
      const averageScore = mainStats.average_score;
  
      // dummy value for case no stat avaialble
      function addDummyIfZero(data, labels) {
        if (data.every((value) => value === 0)) {
          data.push(1);
          labels.push("No Data");
        }
      }

      // Games Won/Lost Data
      const gamesData = [gamesWon, gamesLost];
      const gamesLabels = ["Games Won", "Games Lost"];
      addDummyIfZero(gamesData, gamesLabels);

      // Points Scored/Conceded Data
      const pointsData = [pointsScored, pointsConceded];
      const pointsLabels = ["Points Scored", "Points Conceded"];
      addDummyIfZero(pointsData, pointsLabels);

      const chartOptions = {
        maintainAspectRatio: false,
        tooltips: {
          backgroundColor: "rgb(255,255,255)",
          bodyFontColor: "#858796",
          borderColor: "#000000",
          borderWidth: 1,
          xPadding: 15,
          yPadding: 15,
          displayColors: false,
          caretPadding: 10,
          filter: function (item, chart) {
            return chart.labels[item.index] !== "No Data";
          },
        },
        legend: {
          display: false,
          labels: {
            filter: (item) =>
              item.text !== undefined && item.text !== "No Data",
          },
        },
        cutoutPercentage: 80,
        animation: {
          animateScale: true,
          animateRotate: true,
        },
        responsive: true,
      };

      // Games Won/Lost Pie Chart
      new Chart(gamesPie, {
        type: "doughnut",
        data: {
          labels: gamesLabels,
          datasets: [
            {
              data: gamesData,
              backgroundColor: ["#007bff", "#ff4d4d"],
              hoverBorderColor: "#000000",
              borderColor: "#000000",
              borderWidth: 2,
            },
          ],
        },
        options: chartOptions,
      });

      // points Scored/Conceded Pie Chart
      new Chart(pointsPie, {
        type: "doughnut",
        data: {
          labels: pointsLabels,
          datasets: [
            {
              data: pointsData,
              backgroundColor: ["#007bff", "#ff4d4d"],
              hoverBorderColor: "#000000",
              borderColor: "#000000",
              borderWidth: 2,
            },
          ],
        },
        options: chartOptions,
      });
    }
}

// if want to use the onload in the html
window.initializeCharts = initializeCharts;