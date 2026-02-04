(function () {
    function parseJSONElement(id) {
        var element = document.getElementById(id);
        if (!element) {
            return null;
        }
        try {
            return JSON.parse(element.textContent || '[]');
        } catch (error) {
            return null;
        }
    }

    function renderTrendChart() {
        var series = parseJSONElement('weekly-series-data');
        if (!series || !Array.isArray(series) || series.length === 0) {
            return;
        }

        if (typeof Chart === 'undefined') {
            console.warn('Chart.js yüklenemedi, grafik oluşturulamadı.');
            return;
        }

        var canvas = document.getElementById('weeklyTrendChart');
        if (!canvas) {
            return;
        }

        var labels = series.map(function (item) {
            return item.label;
        });
        var dropoffs = series.map(function (item) {
            return item.dropoff || 0;
        });
        var payouts = series.map(function (item) {
            return item.payout || 0;
        });
        var earnings = series.map(function (item) {
            return item.total_earnings || 0;
        });

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Dropoff',
                        data: dropoffs,
                        borderColor: '#4caf50',
                        backgroundColor: 'rgba(76, 175, 80, 0.15)',
                        tension: 0.35,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Ödeme (₺)',
                        data: payouts,
                        borderColor: '#1e88e5',
                        backgroundColor: 'rgba(30, 136, 229, 0.15)',
                        tension: 0.35,
                        fill: true,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Toplam Hakediş (₺)',
                        data: earnings,
                        borderColor: '#ffb300',
                        backgroundColor: 'rgba(255, 179, 0, 0.15)',
                        tension: 0.35,
                        fill: false,
                        borderDash: [6, 6],
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 16
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function (context) {
                                var value = context.raw || 0;
                                if (context.dataset.label.indexOf('₺') > -1) {
                                    return context.dataset.label + ': ' + Math.round(value).toLocaleString() + '₺';
                                }
                                return context.dataset.label + ': ' + Math.round(value).toLocaleString() + ' paket';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        position: 'left',
                        grid: {
                            drawBorder: false
                        },
                        ticks: {
                            callback: function (value) {
                                return Math.round(value).toLocaleString();
                            }
                        }
                    },
                    y1: {
                        position: 'right',
                        grid: {
                            drawBorder: false,
                            drawOnChartArea: false
                        },
                        ticks: {
                            callback: function (value) {
                                return Math.round(value).toLocaleString() + '₺';
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    function initTargetForm() {
        var goalForm = document.getElementById('goal-form');
        if (!goalForm) {
            return;
        }

        var goalInput = goalForm.querySelector('input[name="goal"]');
        var feedback = document.getElementById('goal-feedback');
        var progressFill = document.querySelector('[data-goal-progress]');
        var targetDisplay = document.querySelector('[data-goal-target]');
        var targetCard = goalForm.closest('.insight-card--target');
        var currentValue = targetCard ? parseFloat(targetCard.dataset.currentDropoff || '0') : 0;

        var setFeedback = function (message, type) {
            if (!feedback) {
                return;
            }
            feedback.textContent = message;
            feedback.classList.remove('is-success', 'is-error');
            if (type) {
                feedback.classList.add(type);
            }
        };

        goalForm.addEventListener('submit', function (event) {
            event.preventDefault();

            var value = parseFloat(goalInput.value);
            if (Number.isNaN(value) || value < 0) {
                setFeedback('Lütfen geçerli bir hedef girin.', 'is-error');
                return;
            }

            var formData = new FormData(goalForm);

            fetch('/api/targets', {
                method: 'POST',
                body: formData
            }).then(function (response) {
                return response.json().then(function (data) {
                    return { ok: response.ok, data: data };
                });
            }).then(function (result) {
                if (!result.ok || !result.data.success) {
                    setFeedback((result.data && result.data.message) || 'Hedef güncellenemedi.', 'is-error');
                    return;
                }

                var goalValue = result.data.goal || 0;
                if (targetDisplay) {
                    targetDisplay.textContent = Math.round(goalValue);
                }
                if (progressFill) {
                    var progress = goalValue > 0 ? Math.min(100, (currentValue / goalValue) * 100) : 0;
                    progressFill.style.width = progress + '%';
                }
                setFeedback('Hedefin güncellendi.', 'is-success');
            }).catch(function () {
                setFeedback('Bir hata oluştu, lütfen tekrar dene.', 'is-error');
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        renderTrendChart();
        initTargetForm();
    });
})();
