<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign Analysis 🌸</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Libraries for Functionality -->
    <script src="https://unpkg.com/react@17/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/papaparse@5.4.1/papaparse.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

    <style>
        body { 
            font-family: 'Inter', sans-serif; 
        }
        .plotly-container {
            border-radius: 0.75rem; 
            padding: 1rem;
            border: 1px solid rgba(210, 231, 218, 0.9); /* Soft green border */
            background-color: rgba(255, 255, 255, 0.6); 
        }
        .filter-select, .filter-input {
            background-color: rgba(255, 255, 255, 0.8);
            border-color: rgba(210, 231, 218, 1); 
            color: #4A6151; /* Dark green text */
            font-weight: 500;
        }
        .filter-select option {
            background-color: #F0F9F3; /* Lighter green for options */
            color: #4A6151; /* Dark green text */
        }
        ::-webkit-calendar-picker-indicator { filter: none; }
        .dashboard-section {
            margin-bottom: 2rem;
            padding: 1.5rem;
            background-color: rgba(255, 255, 255, 0.7); /* More opaque white */
            border-radius: 0.75rem; 
            box-shadow: 0 6px 12px -2px rgba(100,100,100,0.05), 0 3px 7px -3px rgba(100,100,100,0.04); 
            border: 1px solid rgba(255, 255, 255, 0.9);
        }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: rgba(240, 249, 243, 0.5); border-radius: 10px; }
        ::-webkit-scrollbar-thumb { background: rgba(168, 216, 185, 0.8); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(134, 194, 156, 1); }

        @keyframes drift {
            from { transform: translateY(0vh) translateX(0vw) rotate(0deg); }
            to { transform: translateY(110vh) translateX(var(--tx-end)) rotate(var(--rotate-end)); }
        }
        .animate-drift {
            --tx-end: 0vw;
            --rotate-end: 0deg;
            animation-name: drift;
            animation-timing-function: linear;
            animation-iteration-count: infinite;
        }
    </style>
</head>
<body class="bg-gradient-to-br from-pink-100 via-yellow-50 to-green-100">

    <div id="root"></div>

    <script type="text/babel">
        // Main App component
        const App = () => {
            const { useState, useEffect, useRef } = React;
            
            // State to hold the original parsed data from the CSV
            const [data, setData] = useState([]);
            // State to hold the data after cleaning and filtering
            const [filteredData, setFilteredData] = useState([]);
            // State to manage the current filter selections
            const [filters, setFilters] = useState({
                platform: 'All',
                sentiment: 'All',
                mediaType: 'All',
                location: 'All',
                startDate: '',
                endDate: '',
            });
            // State to track if libraries are loaded (they are loaded in head, so this is for logic sequencing)
            const [scriptsLoaded, setScriptsLoaded] = useState(false);
            // State to show loading message during file processing or PDF export
            const [loading, setLoading] = useState(false);
            const [pdfExporting, setPdfExporting] = useState(false);
            // State to hold any error messages
            const [error, setError] = useState('');
            // State for Campaign Strategy Summary
            const [campaignSummary, setCampaignSummary] = useState(
                "Based on the current data, the key actions should focus on leveraging [Top Platform]'s high engagement by increasing content frequency and exploring more [Most Common Media Type] formats. Additionally, targeted campaigns for [Top Location 1] could yield significant results. Addressing negative sentiment proactively and optimizing content for platforms with lower engagement are also crucial steps. More detailed strategies can be formulated once specific campaign goals are defined."
            );

            // Refs for Plotly chart divs
            const sentimentChartRef = useRef(null);
            const engagementTrendChartRef = useRef(null);
            const platformChartRef = useRef(null);
            const mediaTypeChartRef = useRef(null);
            const locationChartRef = useRef(null);
            // Ref for the main dashboard content to be exported to PDF
            const dashboardContentRef = useRef(null);

            // Hardcoded insights for each chart
            const insights = {
                sentiment: [
                    "Insight 1: ✨ The majority of content generates positive sentiment, indicating strong brand appeal.",
                    "Insight 2: 🤔 A small percentage of negative sentiment exists, which could be an opportunity to address specific customer concerns.",
                    "Insight 3: 💡 Neutral sentiment posts might benefit from content adjustments to drive stronger emotional responses."
                ],
                engagementTrend: [
                    "Insight 1: 📈 Engagements show a general upward trend over time, suggesting growing audience interest or effective long-term strategies.",
                    "Insight 2: 🚀 Significant spikes in engagement often correlate with specific campaigns or viral content, highlighting successful initiatives.",
                    "Insight 3: 🧐 Identifying periods of low engagement can help in optimizing content scheduling or exploring new content formats."
                ],
                platformEngagements: [
                    "Insight 1: 🏆 [Top Platform] consistently drives the highest engagement, making it a primary channel for content distribution.",
                    "Insight 2: 🛠️ Platforms with lower engagement might require a revised content strategy tailored to their audience demographics.",
                    "Insight 3: 🌐 Diversifying content across multiple platforms helps reach a broader audience, even if engagement varies."
                ],
                mediaTypeMix: [
                    "Insight 1: 🌟 [Most Common Media Type] is the most frequently used and likely preferred content format by the audience.",
                    "Insight 2: 🎨 Exploring underutilized media types could uncover new avenues for audience engagement and content innovation.",
                    "Insight 3: 🔄 A balanced mix of media types can cater to diverse audience preferences and keep content fresh."
                ],
                topLocations: [
                    "Insight 1: 📍 [Top Location 1] and [Top Location 2] are key geographical hubs for engagement, indicating strong regional interest.",
                    "Insight 2: 🎯 Tailoring content or campaigns to specific top locations could further enhance local relevance and engagement.",
                    "Insight 3: 🌍 Understanding the demographics and cultural nuances of top engaging locations can inform future marketing efforts."
                ]
            };

            // Check for scripts on mount
            useEffect(() => {
                if (window.React && window.ReactDOM && window.Papa && window.Plotly && window.jspdf && window.html2canvas) {
                    setScriptsLoaded(true);
                } else {
                    setError("Some required libraries failed to load. Please refresh the page.");
                }
            }, []);

            // Effect to apply filters
            useEffect(() => {
                if (data.length > 0) {
                    applyFilters();
                }
            }, [data, filters]);

            // Effect to generate charts
            useEffect(() => {
                if (filteredData.length > 0 && scriptsLoaded) {
                    generateCharts();
                } else if (scriptsLoaded && data.length > 0 && filteredData.length === 0) {
                    clearCharts();
                }
            }, [filteredData, scriptsLoaded]);

            // Function to clear charts
            const clearCharts = () => {
                if (window.Plotly) {
                    [sentimentChartRef, engagementTrendChartRef, platformChartRef, mediaTypeChartRef, locationChartRef].forEach(ref => {
                        if (ref.current && ref.current.data) {
                            try {
                                Plotly.purge(ref.current);
                            } catch (e) {
                                console.warn("Error purging chart:", e);
                            }
                        }
                    });
                }
            };

            // Handler for CSV file upload
            const handleFileUpload = (event) => {
                const file = event.target.files[0];
                if (!file) return;
                if (file.type !== 'text/csv') {
                    setError('🌸 Please upload a CSV file.');
                    return;
                }
                setLoading(true);
                setError('');
                setData([]);
                setFilteredData([]);
                clearCharts();

                window.Papa.parse(file, {
                    header: true,
                    skipEmptyLines: true,
                    complete: (results) => {
                        if (results.errors.length > 0) {
                            console.error("CSV Parsing Errors:", results.errors);
                            setError(`❌ Error parsing CSV: ${results.errors[0].message}. Please check CSV format.`);
                            setLoading(false);
                            return;
                        }
                        const cleanedData = results.data.map(row => ({
                            ...row,
                            Date: row.Date ? new Date(row.Date) : null,
                            Engagements: row.Engagements ? parseFloat(row.Engagements) : 0,
                            'Sentiment Score': row['Sentiment Score'] ? parseFloat(row['Sentiment Score']) : 0,
                            Platform: row.Platform || 'N/A',
                            Sentiment: row.Sentiment || 'N/A',
                            'Media Type': row['Media Type'] || 'N/A',
                            Location: row.Location || 'N/A',
                        })).filter(row => row.Date !== null && !isNaN(row.Date.getTime()));

                        if (cleanedData.length === 0 && results.data.length > 0) {
                             setError('⚠️ No valid date entries found. Charts may not display correctly.');
                        } else if (cleanedData.length === 0) {
                             setError('⚠️ No data parsed or data is not in the expected format.');
                        }
                        setData(cleanedData);
                        setLoading(false);
                    },
                    error: (err) => {
                        setError(`❌ Error parsing CSV: ${err.message}`);
                        setLoading(false);
                    }
                });
            };

            // Function to apply filters
            const applyFilters = () => {
                let currentFilteredData = [...data];
                if (filters.platform !== 'All') {
                    currentFilteredData = currentFilteredData.filter(d => d.Platform === filters.platform);
                }
                if (filters.sentiment !== 'All') {
                    currentFilteredData = currentFilteredData.filter(d => d.Sentiment === filters.sentiment);
                }
                if (filters.mediaType !== 'All') {
                    currentFilteredData = currentFilteredData.filter(d => d['Media Type'] === filters.mediaType);
                }
                if (filters.location !== 'All') {
                    currentFilteredData = currentFilteredData.filter(d => d.Location === filters.location);
                }
                if (filters.startDate) {
                    const start = new Date(filters.startDate);
                    start.setHours(0, 0, 0, 0);
                    currentFilteredData = currentFilteredData.filter(d => d.Date && d.Date >= start);
                }
                if (filters.endDate) {
                    const end = new Date(filters.endDate);
                    end.setHours(23, 59, 59, 999);
                    currentFilteredData = currentFilteredData.filter(d => d.Date && d.Date <= end);
                }
                setFilteredData(currentFilteredData);
            };

            // Handler for filter changes
            const handleFilterChange = (e) => {
                const { name, value } = e.target;
                setFilters(prevFilters => ({ ...prevFilters, [name]: value }));
            };

            // Handler for clearing filters
            const handleClearFilters = () => {
                setFilters({
                    platform: 'All', sentiment: 'All', mediaType: 'All',
                    location: 'All', startDate: '', endDate: '',
                });
                setError('');
            };
            
            // Function to generate charts
            const generateCharts = () => {
                if (!window.Plotly || !filteredData.length) {
                    clearCharts();
                    return;
                }
                const baseLayout = {
                    height: 400, showlegend: true, margin: { t: 60, b: 60, l: 70, r: 50 },
                    font: { family: 'Inter, sans-serif', color: '#5D7A68' },
                    paper_bgcolor: 'rgba(255, 255, 255, 0.7)', plot_bgcolor: 'rgba(240, 249, 243, 0.7)',
                    titlefont: { color: '#4A6151', size: 18 },
                    xaxis: { titlefont: { color: '#5D7A68', size: 14 }, tickfont: { color: '#5D7A68' }, gridcolor: 'rgba(209, 227, 216, 0.5)', linecolor: 'rgba(156, 175, 163, 0.7)' },
                    yaxis: { titlefont: { color: '#5D7A68', size: 14 }, tickfont: { color: '#5D7A68' }, gridcolor: 'rgba(209, 227, 216, 0.5)', linecolor: 'rgba(156, 175, 163, 0.7)' },
                    legend: { font: { color: '#5D7A68' }, bgcolor: 'rgba(255, 255, 255, 0.5)', bordercolor: 'rgba(209, 227, 216, 0.7)' }
                };
                const pieChartMarkerColors = ['#FADADD', '#FFF2CC', '#D4EDDA', '#E8DAEF', '#D1E8F6'];
                const barChartColor1 = '#A8D8B9';
                const barChartColor2 = '#F8C8DC';
                const lineChartColor = '#B0C2F2';

                // --- Sentiment Breakdown ---
                const sentimentCounts = filteredData.reduce((acc, curr) => { acc[curr.Sentiment] = (acc[curr.Sentiment] || 0) + 1; return acc; }, {});
                if (sentimentChartRef.current) Plotly.react(sentimentChartRef.current, [{ labels: Object.keys(sentimentCounts), values: Object.values(sentimentCounts), type: 'pie', hole: 0.4, marker: { colors: pieChartMarkerColors }, textfont: { color: '#4A6151', size: 12 } }], { ...baseLayout, title: 'Sentiment Breakdown 🌸' });

                // --- Engagement Trend ---
                const engagementByDate = filteredData.reduce((acc, curr) => { const dateStr = curr.Date ? curr.Date.toISOString().split('T')[0] : 'Unknown'; if (dateStr !== 'Unknown') acc[dateStr] = (acc[dateStr] || 0) + curr.Engagements; return acc; }, {});
                const sortedDates = Object.keys(engagementByDate).sort((a, b) => new Date(a) - new Date(b));
                if (engagementTrendChartRef.current) Plotly.react(engagementTrendChartRef.current, [{ x: sortedDates, y: sortedDates.map(date => engagementByDate[date]), mode: 'lines+markers', name: 'Engagements', line: { color: lineChartColor, width: 2.5 }, marker: { size: 8, color: '#FADADD' } }], { ...baseLayout, title: 'Engagement Trend 📈', xaxis: { ...baseLayout.xaxis, type: 'date', title: 'Date' }, yaxis: { ...baseLayout.yaxis, title: 'Total Engagements' } });
                
                // --- Platform Engagements ---
                const platformEngagements = filteredData.reduce((acc, curr) => { acc[curr.Platform] = (acc[curr.Platform] || 0) + curr.Engagements; return acc; }, {});
                if (platformChartRef.current) Plotly.react(platformChartRef.current, [{ x: Object.keys(platformEngagements), y: Object.values(platformEngagements), type: 'bar', marker: { color: barChartColor1 } }], { ...baseLayout, title: 'Platform Engagements 🚀', xaxis: { ...baseLayout.xaxis, title: 'Platform' }, yaxis: { ...baseLayout.yaxis, title: 'Total Engagements' } });

                // --- Media Type Mix ---
                const mediaTypeCounts = filteredData.reduce((acc, curr) => { acc[curr['Media Type']] = (acc[curr['Media Type']] || 0) + 1; return acc; }, {});
                if (mediaTypeChartRef.current) Plotly.react(mediaTypeChartRef.current, [{ labels: Object.keys(mediaTypeCounts), values: Object.values(mediaTypeCounts), type: 'pie', hole: 0.4, marker: { colors: pieChartMarkerColors }, textfont: { color: '#4A6151', size: 12 } }], { ...baseLayout, title: 'Media Type Mix 🎨' });

                // --- Top 5 Locations ---
                const locationEngagements = filteredData.reduce((acc, curr) => { acc[curr.Location] = (acc[curr.Location] || 0) + curr.Engagements; return acc; }, {});
                const sortedLocations = Object.entries(locationEngagements).sort(([, a], [, b]) => b - a).slice(0, 5);
                if (locationChartRef.current) Plotly.react(locationChartRef.current, [{ x: sortedLocations.map(([loc]) => loc), y: sortedLocations.map(([, eng]) => eng), type: 'bar', marker: { color: barChartColor2 } }], { ...baseLayout, title: 'Top 5 Locations 🌍', xaxis: { ...baseLayout.xaxis, title: 'Location' }, yaxis: { ...baseLayout.yaxis, title: 'Total Engagements' } });
            };
            
            // Helper to get unique values for dropdowns
            const getUniqueValues = (key) => [...new Set(data.map(item => item[key]))].filter(Boolean).sort();
            
            // Dynamic insight helpers
            const getTopPlatform = () => { if (!filteredData.length) return "[Platform]"; const p = filteredData.reduce((acc, curr) => { acc[curr.Platform] = (acc[curr.Platform] || 0) + curr.Engagements; return acc; }, {}); return Object.entries(p).sort(([, a], [, b]) => b - a)[0]?.[0] || "[Platform]"; };
            const getMostCommonMediaType = () => { if (!filteredData.length) return "[Media Type]"; const mt = filteredData.reduce((acc, curr) => { acc[curr['Media Type']] = (acc[curr['Media Type']] || 0) + 1; return acc; }, {}); return Object.entries(mt).sort(([, a], [, b]) => b - a)[0]?.[0] || "[Media Type]"; };
            const getTopLocations = () => { if (!filteredData.length) return ["[Location]", ""]; const l = filteredData.reduce((acc, curr) => { acc[curr.Location] = (acc[curr.Location] || 0) + curr.Engagements; return acc; }, {}); const sorted = Object.entries(l).filter(([loc]) => loc && loc !== 'N/A').sort(([, a], [, b]) => b - a).slice(0, 2).map(([loc]) => loc); return sorted.length > 0 ? sorted : ["[Location]", ""]; };

            // Function to handle PDF export
            const handleExportToPDF = async () => {
                if (!dashboardContentRef.current) return;
                setPdfExporting(true);
                setError('');
                try {
                    const { jsPDF } = window.jspdf;
                    const canvas = await window.html2canvas(dashboardContentRef.current, { scale: 2, useCORS: true, backgroundColor: '#fdfbf6', logging: false });
                    const imgData = canvas.toDataURL('image/png');
                    const pdf = new jsPDF({ orientation: 'p', unit: 'px', format: [canvas.width, canvas.height] });
                    pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
                    pdf.save('campaign-analysis-dashboard.pdf');
                } catch (e) {
                    console.error("Error exporting to PDF:", e);
                    setError(`❌ Failed to export to PDF: ${e.message}`);
                } finally {
                    setPdfExporting(false);
                }
            };
            
            // Flower component for background effect
            const Flower = ({ style, children }) => {
                const newStyle = {
                    ...style,
                    '--tx-end': `${Math.random() * 8 - 4}vw`,
                    '--rotate-end': `${Math.random() * 360}deg`
                };
                return <span className="absolute text-xl animate-drift" style={newStyle}>{children}</span>;
            };

            const flowers = ['🌸', '🌼', '🌷', '🌿', '🌻'].flatMap((emoji, emojiIndex) => 
                Array.from({ length: 4 }).map((_, i) => ({
                    id: emojiIndex * 4 + i, emoji: emoji,
                    style: { top: `-10%`, left: `${Math.random() * 100}%`, animationDelay: `${Math.random() * 15}s`, animationDuration: `${10 + Math.random() * 10}s`, opacity: `${0.4 + Math.random() * 0.4}` }
                }))
            );

            return (
                <div className="relative min-h-screen p-4 overflow-hidden">
                    <div className="absolute inset-0 z-0 pointer-events-none">
                        {flowers.map(flower => <Flower key={flower.id} style={flower.style}>{flower.emoji}</Flower>)}
                    </div>
                    
                    <div ref={dashboardContentRef} className="relative z-10 max-w-7xl mx-auto bg-white/40 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/60">
                        <div className="flex justify-between items-center mb-2">
                            <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-500 via-pink-400 to-yellow-500">
                                Campaign Analysis 🌸
                            </h1>
                        </div>
                        <p className="text-center text-green-600 mb-8 text-base">Visualizing campaign performance and extracting actionable insights. 🌿</p>

                        <div className="dashboard-section">
                            <label htmlFor="csv-upload" className="block text-lg font-semibold text-green-800 mb-3">Upload your CSV Data File 📜</label>
                            <input type="file" id="csv-upload" accept=".csv" onChange={handleFileUpload} className="block w-full text-sm text-gray-600 file:mr-4 file:py-2.5 file:px-5 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-pink-300 file:text-white hover:file:bg-pink-400 transition-colors duration-200 cursor-pointer" />
                            {loading && <p className="mt-3 text-green-600 animate-pulse">⏳ Processing data... Please wait a moment.</p>}
                            {error && <p className="mt-3 text-red-500 font-semibold text-base">{error}</p>}
                            {data.length > 0 && !loading && !error && <p className="mt-3 text-green-700 font-medium">✅ Success! {data.length} records loaded and visualized below.</p>}
                        </div>

                        {data.length > 0 && (
                            <div className="dashboard-section">
                                <h2 className="text-2xl font-semibold text-green-800 mb-5">Filter Your Data 🧪</h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-4 mb-4">
                                    {['Platform', 'Sentiment', 'Media Type', 'Location'].map(key => {
                                        const name = key.toLowerCase().replace(/ /g, '') === 'mediatype' ? 'mediaType' : key.toLowerCase();
                                        return (
                                            <div className="flex flex-col" key={key}>
                                                <label htmlFor={name} className="text-sm font-medium text-green-700 mb-1.5">{key}</label>
                                                <select id={name} name={name} value={filters[name]} onChange={handleFilterChange} className="p-2.5 border rounded-md shadow-sm focus:ring-green-400 focus:border-green-400 filter-select">
                                                    <option value="All">All {key}s</option>
                                                    {getUniqueValues(key).map(option => <option key={option} value={option}>{option}</option>)}
                                                </select>
                                            </div>
                                        );
                                    })}
                                    <div className="flex flex-col">
                                        <label htmlFor="startDate" className="text-sm font-medium text-green-700 mb-1.5">Start Date</label>
                                        <input type="date" id="startDate" name="startDate" value={filters.startDate} onChange={handleFilterChange} className="p-2.5 border rounded-md shadow-sm focus:ring-green-400 focus:border-green-400 filter-input" />
                                    </div>
                                    <div className="flex flex-col">
                                        <label htmlFor="endDate" className="text-sm font-medium text-green-700 mb-1.5">End Date</label>
                                        <input type="date" id="endDate" name="endDate" value={filters.endDate} onChange={handleFilterChange} className="p-2.5 border rounded-md shadow-sm focus:ring-green-400 focus:border-green-400 filter-input" />
                                    </div>
                                </div>
                                <button onClick={handleClearFilters} className="mt-4 px-6 py-2.5 bg-yellow-300 text-yellow-800 font-semibold rounded-lg shadow-sm hover:bg-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:ring-opacity-75 transition duration-200">Clear Filters ✨</button>
                            </div>
                        )}

                        {filteredData.length > 0 && scriptsLoaded && (
                            <div className="dashboard-section">
                                <h2 className="text-2xl font-semibold text-green-800 mb-6 text-center">Campaign Visualizations 📊</h2>
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                    {[ { ref: sentimentChartRef, insightsKey: 'sentiment', title: "Sentiment Analysis" }, { ref: engagementTrendChartRef, insightsKey: 'engagementTrend', title: "Engagement Over Time" }, { ref: platformChartRef, insightsKey: 'platformEngagements', title: "Platform Performance" }, { ref: mediaTypeChartRef, insightsKey: 'mediaTypeMix', title: "Content Mix" }, { ref: locationChartRef, insightsKey: 'topLocations', title: "Geographic Hotspots" }, ].map(({ ref, insightsKey, title }) => (
                                        <div className="plotly-container shadow-md" key={insightsKey}>
                                            <div ref={ref} className="w-full h-96"></div>
                                            <h3 className="text-lg font-semibold text-green-700 mt-4 mb-2">{title} - Insights:</h3>
                                            <ul className="list-disc list-inside text-green-800 text-sm space-y-1.5">
                                                {insights[insightsKey].map((insight, index) => (
                                                    <li key={index}>
                                                        {insight.replace('[Top Platform]', getTopPlatform()).replace('[Most Common Media Type]', getMostCommonMediaType()).replace('[Top Location 1]', getTopLocations()[0] || 'N/A').replace('[Top Location 2]', getTopLocations()[1] || 'N/A')}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        
                        {data.length > 0 && (
                            <div className="dashboard-section">
                                <h2 className="text-2xl font-semibold text-green-800 mb-4">Campaign Strategy Summary 📝</h2>
                                <p className="text-green-700 text-base leading-relaxed">
                                    {campaignSummary.replace('[Top Platform]', getTopPlatform()).replace('[Most Common Media Type]', getMostCommonMediaType()).replace('[Top Location 1]', getTopLocations()[0] || 'N/A')}
                                </p>
                            </div>
                        )}

                        {filteredData.length > 0 && scriptsLoaded && !loading && (
                            <div className="mt-6 mb-8 text-center">
                                <button onClick={handleExportToPDF} disabled={pdfExporting} className="px-6 py-3 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-75 transition duration-200 disabled:opacity-60 disabled:cursor-not-allowed">
                                    {pdfExporting ? 'Exporting PDF... ⏳' : 'Export to PDF 📄'}
                                </button>
                            </div>
                        )}

                        {filteredData.length === 0 && data.length > 0 && !loading && (
                            <div className="mt-8 p-6 bg-yellow-100 rounded-lg shadow-inner text-center text-yellow-700 border border-yellow-200">
                                <p className="text-lg font-medium">🤷‍♀️ No data matches the current filter criteria.</p>
                                <p className="text-sm mt-2">Try adjusting your filters or clearing them!</p>
                            </div>
                        )}
                        {!scriptsLoaded && !error && !loading && (
                            <div className="mt-8 p-6 bg-gray-100 rounded-lg shadow-inner text-center text-gray-600">
                                <p className="text-lg font-medium animate-pulse">🌱 Loading visualization tools...</p>
                            </div>
                        )}

                        {scriptsLoaded && (data.length > 0 || error) && !loading && (
                            <div className="mt-12 text-center">
                                <p className="text-pink-500 text-lg mb-4">Hope this analysis is helpful! 🌷</p>
                                <p className="text-green-700 text-xs">Made by Zulfa Nur Aina Putri</p>
                            </div>
                        )}
                    </div>
                </div>
            );
        };

        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>
