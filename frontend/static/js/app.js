// Main application JavaScript
document.addEventListener('DOMContentLoaded', function () {
    // Add any global JavaScript functionality here
    console.log('RetailMind loaded');

    // Add loading states to buttons
    const buttons = document.querySelectorAll('button[type="button"], .btn-refresh');
    buttons.forEach(button => {
        button.addEventListener('click', function (e) {
            const originalText = this.textContent;
            this.textContent = 'Loading...';
            this.disabled = true;

            // Restore after 2 seconds if still loading
            setTimeout(() => {
                if (this.textContent === 'Loading...') {
                    this.textContent = originalText;
                    this.disabled = false;
                }
            }, 2000);
        });
    });

    // Handle navigation active state
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.fontWeight = 'bold';
            link.style.color = '#2c3e50';
        }
    });
});

// Simulator Tabs
function switchSimTab(tabName) {
    // Hide all panels
    ['price', 'promo', 'stock', 'competitor', 'marketing'].forEach(t => {
        const p = document.getElementById(`sim-panel-${t}`);
        if (p) p.classList.add('hidden');
    });

    // Show active panel
    document.getElementById(`sim-panel-${tabName}`).classList.remove('hidden');

    // Update tab styling
    document.querySelectorAll('.sim-tab').forEach(btn => {
        btn.classList.remove('active');
        // Simple text matching
        let txt = btn.textContent.toLowerCase();
        if ((tabName === 'stock' && txt.includes('inventory')) ||
            (tabName === 'competitor' && txt.includes('competitor')) ||
            (tabName === 'marketing' && txt.includes('ads')) ||
            (txt.includes(tabName))) {
            btn.classList.add('active');
        }
    });

    // Hide previous results
    document.getElementById('simulation-result').classList.add('hidden');
}

// Simulation Logic
async function runSimulation(type) {
    const productName = document.querySelector('h1').textContent.replace('🔍 ', '');
    const resultDiv = document.getElementById('simulation-result');
    const extraMetricsDiv = document.getElementById('sim-extra-metrics');

    // Identify active button
    const visibleBtn = Array.from(document.querySelectorAll('.btn-sim')).find(b => b.offsetParent !== null);
    if (visibleBtn) {
        visibleBtn.textContent = 'Simulating...';
        visibleBtn.disabled = true;
    }

    let params = {};
    if (type === 'price_change') {
        params = { new_price: document.getElementById('sim-price').value };
    } else if (type === 'promotion') {
        params = {
            discount_pct: document.getElementById('sim-discount').value,
            duration_days: document.getElementById('sim-duration').value
        };
    } else if (type === 'inventory_change') {
        params = { new_stock_units: document.getElementById('sim-stock').value };
    } else if (type === 'competitor_move') {
        params = { competitor_drop_pct: document.getElementById('sim-comp-drop').value };
    } else if (type === 'marketing') {
        params = {
            ad_spend: document.getElementById('sim-ad-spend').value,
            lift_pct: document.getElementById('sim-ad-lift').value
        };
    }

    try {
        const queryParams = new URLSearchParams(params).toString();
        const response = await fetch(`/api/v1/simulator/${encodeURIComponent(productName)}/${type}?${queryParams}`);
        const result = await response.json();

        resultDiv.classList.remove('hidden');
        extraMetricsDiv.innerHTML = '';
        extraMetricsDiv.classList.add('hidden');

        // Common Elements
        const revElem = document.getElementById('sim-revenue-change');
        const demElem = document.getElementById('sim-demand-change');
        const recElem = document.getElementById('sim-recommendation');

        // Reset colors
        revElem.className = 'sim-value';

        if (type === 'price_change') {
            revElem.textContent = (result.revenue_change_pct > 0 ? '+' : '') + result.revenue_change_pct + '%';
            revElem.style.color = result.revenue_change_pct > 0 ? '#27ae60' : '#e74c3c';
            demElem.textContent = (result.demand_change_pct > 0 ? '+' : '') + result.demand_change_pct + '%';
            recElem.textContent = `AI Advice: ${result.recommendation} price change.`;

        } else if (type === 'promotion') {
            revElem.textContent = (result.revenue_impact > 0 ? '+' : '') + '$' + result.revenue_impact;
            revElem.style.color = result.is_profitable ? '#27ae60' : '#e74c3c';
            demElem.textContent = '+' + result.lift_pct + '% (Lift)';
            recElem.textContent = `AI Advice: ${result.recommendation} this promotion.`;

        } else if (type === 'inventory_change') {
            revElem.textContent = 'N/A';
            demElem.textContent = 'N/A';
            extraMetricsDiv.classList.remove('hidden');
            extraMetricsDiv.innerHTML = `
                <div><span>Holding Cost:</span> <span class="sim-value" style="color:${result.holding_cost_change > 0 ? '#e74c3c' : '#27ae60'}">${result.holding_cost_change > 0 ? '+' : ''}$${result.holding_cost_change}</span></div>
                <div><span>Stockout Risk:</span> <span class="sim-value" style="color:#27ae60">-${result.stockout_risk_reduction}%</span></div>
            `;
            recElem.textContent = `AI Advice: ${result.recommendation} inventory level.`;

        } else if (type === 'competitor_move') {
            revElem.textContent = result.revenue_impact_pct + '%';
            revElem.style.color = '#e74c3c'; // usually bad
            demElem.textContent = result.demand_impact_pct + '%';
            recElem.textContent = `Strategy: ${result.recommendation}`;

        } else if (type === 'marketing') {
            // Marketing returns daily lift and BEP
            revElem.textContent = '+$' + result.daily_revenue_increase + '/day';
            revElem.style.color = '#27ae60';
            demElem.textContent = '+' + result.traffic_lift_pct + '%';

            extraMetricsDiv.classList.remove('hidden');
            extraMetricsDiv.innerHTML = `
                <div><span>Break Even:</span> <span class="sim-value">${result.break_even_days} Days</span></div>
            `;
            recElem.textContent = `Advice: ${result.recommendation} (Ads pay off in ${result.break_even_days} days)`;
        }

    } catch (error) {
        console.error('Simulation failed:', error);
        alert('Simulation failed. Please try again.');
    } finally {
        if (visibleBtn) {
            visibleBtn.textContent = 'Simulate';
            visibleBtn.disabled = false;
        }
    }
}