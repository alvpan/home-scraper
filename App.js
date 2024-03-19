import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import ReactApexChart from 'react-apexcharts';
import axios from 'axios';

function App() {

  const [squareMeters, setSquareMeters] = useState('');
  const [euros, setEuros] = useState('');
  const [eurosPerSqMeter, setEurosPerSqMeter] = useState(null);

  // Add a function to determine if a select should have the 'selected' class
  const isSelectedClass = (value) => value ? 'selected' : '';

  // Function to create the combined string
  const getCombinedString = () => {
    if (selection.action && selection.location) {
      return `${selection.action}_${selection.location}${province ? `_${province}` : ''}`;
    }
    return '';
  };

  const [cityData, setCityData] = useState({
    cities: [],
    provinces: {}
  });

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/cities_hierarchy')
      .then(response => {
        const data = response.data; // JSON data
  
        let cities = [];
        let provinces = {};
  
        // Adding cities under 'City'
        if (data['City']) {
          cities = [...data['City']];
        }
  
        // Iterating over the keys to add parent cities and set provinces
        Object.keys(data).forEach(key => {
          // Add the key (parent city) to the cities array
          if (key !== 'City') {
            cities.push(key);
          }
          // Setting provinces for each parent city
          provinces[key] = data[key];
        });
  
        setCityData({ cities, provinces });
      })
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  const [province, setProvince] = useState('');
  const [selection, setSelection] = useState({
    action: '',
    location: ''
  });

  const handleButtonClick = (action) => {
    setSelection({ ...selection, action });
  };

  const [selectedSize, setSelectedSize] = useState('');

  const generateSizeOptions = () => {
    let options = [];
    for (let i = 20; i <= 1000; i += 5) {
      options.push(<option key={i} value={i}>{i} m²</option>);
    }
    return options;
  };
  
  const chartRef = useRef(null);
  const [showChart, setShowChart] = useState(false);

  const [isLoadingChart, setIsLoadingChart] = useState(true); // For the first chart
  const [isLoadingPPMChart, setIsLoadingPPMChart] = useState(true); // For the ppmChart

  const [chartData, setChartData] = useState({
    options: {
      chart: {
        type: 'area',
        background: 'transparent',
        toolbar: {
          show: false,
        },
        zoom: {
          enabled: false,
        }
      },
      tooltip: {
        marker: {
          show: false,
        },
        style: {
          fontSize: '20px',
          fontFamily: undefined,
          colors: ['black']
        }
      },
      markers: {
        size: 4,
        colors: ['orange'],
        strokeColors: 'orange',
        radious: 10,
        strokeWidth: 5
      },
      stroke: {
        curve: 'smooth'
      },
      dataLabels: {
        enabled: false
      },
      title: {
        text: 'Latest Average Price per Property Size',
        align: 'center',
        style: {
          fontSize: '16px',
          color: 'white',
          fontFamily: 'Consolas'
        }  
      },
      xaxis: {
        labels: {
          rotatae: -45,
          style: {
            colors: 'white',
            fontSize: '12px'
          }
        },
        title: {
          style: {
            fontSize: '16px',
            color: 'white',
            fontFamily: 'Consolas'
          }
        },
      },
      yaxis: {
        forceNiceScale: true,
        labels: {
          style: {
            colors: 'white',
            fontSize: '12px'
          }
        }
      },
      colors: ['orange'],
    },
    series: [
      {
        name: '€',
        data: [], // Initially empty data
      }
    ]
  });

  const [ppmChartData, setPpmChartData] = useState({
    options: {
      chart: {
        toolbar: {
          show: false
        },
        zoom: {
          enabled: false,
        }
      },
      markers: {
        size: 4,
        colors: ['white'],
        strokeColors: 'white',
        radious: 10,
        strokeWidth: 5
      },
      stroke: {
        curve: 'smooth'
      },
      dataLabels: {
        enabled: true,
        style: {
          fontSize: '20px',
          fontFamily: 'Helvetica, Arial, sans-serif',
          fontWeight: 'bold',
          colors: ['orange']
        }
      },
      tooltip: {
        marker: {
          show: false,
        },
        style: {
          fontSize: '20px',
          fontFamily: undefined,
          colors: ['black'] 
        }
      },
      title: {
        text: 'Last Month Prices for selected sqm',
        align: 'center',
        style: {
          fontSize: '16px',
          color: 'white',
          fontFamily: 'Consolas'
        }  
      },
      xaxis: {
        // type: 'datetime',
        categories: [],
        labels: {
          style: {
            colors: 'white',
            fontSize: '12px'
          }
        },
        title: {
          style: {
            fontSize: '16px',
            color: 'white',
            fontFamily: 'Consolas'
          }
        },
      },
      yaxis: {
        min: 0,
        forceNiceScale: true,
        labels: {
          style: {
            colors: 'white',
            fontSize: '12px'
          }
        }
      },
      colors: ['orange'],
    },
    series: [
      {
        name: '€',
        data: [],
      }
    ]
  });
  
  const handleSelectChange = (e) => {
    setSelection({ ...selection, location: e.target.value });
    setProvince(''); // Reset province when city changes
    setShowChart(false); // Hide the chart when a new city is selected
  };

  const [fetchedData, setFetchedData] = useState(null);

  const [ppmValue, setPpmValue] = useState(null);

  const [percentageDifference, setPercentageDifference] = useState(null);

  const handleEvaluateClick = () => {
    if (squareMeters && euros) {
      const calculation = Number(euros) / Number(squareMeters);
      setEurosPerSqMeter(calculation.toFixed(2)); // Keeping two decimal places for precision
  
      // Calculate the percentage difference if ppmValue is not null
      if (ppmValue) {
        const percentageDifference = ((calculation - ppmValue) / ppmValue) * 100;
        setPercentageDifference(percentageDifference.toFixed(1));
      }
    } else {
      setEurosPerSqMeter(null);
      setPercentageDifference(null);
    }
  };
  
  const getButtonClass = (buttonAction) => {
    return `selection-button ${selection.action === buttonAction ? 'selected' : 'transparent'}`;
  };

  const [ppmDataError, setPpmDataError] = useState(false);

  const handleSeePricesClick = async () => {
    setShowChart(true);
    setSelectedSize("40"); // Automatically select the 40 m² value
    const tableName = getCombinedString();
    const latestTableNamesEndpoint = `http://127.0.0.1:5000/latest_tables_month/${tableName}`;
  
    try {
      const response = await axios.get(latestTableNamesEndpoint);
      const tableNames = response.data; // This is now an array of table names
  
      if (tableNames.length === 0) {
        console.error('No tables found for the given base name');
        return;
      }
  
      let ppmValues = [];

      // Fetch the first row of each table to extract the ppm value
      for (const currentTableName of tableNames) {
        const url = `http://127.0.0.1:5000/data?table=${currentTableName}`;
        const tableDataResponse = await axios.get(url);
        const fetchedData = tableDataResponse.data;
        if (fetchedData && fetchedData.length > 0) {
          const ppm = fetchedData[0].ppm;
          ppmValues.push(ppm);
        }
      }

      // Parse table names to find the latest one based on date
      const latestTableName = tableNames.reduce((latest, current) => {
        const latestDate = new Date(latest.split('_').slice(-3).join('-'));
        const currentDate = new Date(current.split('_').slice(-3).join('-'));
        return currentDate > latestDate ? current : latest;
      }, tableNames[0]);
  
      const url = `http://127.0.0.1:5000/data?table=${latestTableName}`;
      const tableDataResponse = await axios.get(url);
      const fetchedData = tableDataResponse.data;
  
      setFetchedData(fetchedData);

      // Sort the data based on 'size' in ascending order
      const sortedData = fetchedData.sort((a, b) => a.size - b.size);

      // Process the fetched data
      const sizes = sortedData.map(item => item.size);
      const prices = sortedData.map(item => item.price);
      const ppms = sortedData.map(item => item.ppm);
      const ppm = ppms[0];
      setPpmValue(ppm); // Add this line after you define the ppm variable

      const processDataWithUnits = (data) => {
        return data.map(item => `${item} m²`);
      };

      // Update the chart data
      setChartData(prevData => ({
        ...prevData,
        options: {
            ...prevData.options,
            xaxis: {
                ...prevData.options.xaxis,
                categories: processDataWithUnits(sizes),
            },
        },
        series: [
            {
                name: '€',
                data: prices,
            }
        ]
      }));
      setIsLoadingChart(false); //hide the loading indicator

      // Transform ppmValues and update ppmChartData for the new ApexChart
      const categories = ppmValues.map(item => item.name);
      const data = ppmValues.map(item => item.ppm);

      console.log('Chart Data:', data); // Log the data array to the console

    } catch (error) {
      console.error('Error fetching data:', error);
    }
    fetchDataForSelectedSize();
    setIsLoadingPPMChart(false);
  };

  const inputStyle = {
    WebkitAppearance: 'none',
    MozAppearance: 'textfield',
  };

  const fetchDataForSelectedSize = async () => {

    setIsLoadingPPMChart(true);
    setPpmDataError(false);
  
    const tableName = getCombinedString();
    const selectedSizeValue = selectedSize;
  
    const lastMonthPricesEndpoint = `http://127.0.0.1:5000/last_month_prices/${tableName}/${selectedSizeValue}`;
  
    try {
      const response = await axios.get(lastMonthPricesEndpoint);
      const data = response.data;

      const y_data = data.map(item => item.price);
      const highestDataPoint = Math.max(...y_data);
      const max = highestDataPoint + (highestDataPoint * 0.5);

      const x_data = data.map(item => item.date);
      const latestDataPoint = Math.max(...x_data);
      const max_x = latestDataPoint + (latestDataPoint * 0.2);

      setPpmChartData(prevData => ({
        ...prevData,
        options: {
          ...prevData.options,
          xaxis: {
            // max: max_x,
            ...prevData.options.xaxis,
            categories: data.map(item => item.date),
            // type: 'datetime',
            labels: {
              format: 'dd-MM',
              style: {
                colors: 'white',
                fontSize: '12px'
              }
            }
          },
          yaxis: {
            forceNiceScale: true,
            min: 0,
            max: max,
            labels: {
              style: {
                colors: 'white',
                fontSize: '12px' 
              }
            }
          }
          
          
        },
        series: [{
          ...prevData.series[0],
          data: data.map(item => item.price)
        }]
      }));
    
    setIsLoadingPPMChart(false);
    setPpmDataError(false)
  
  } catch (error) {
      console.error('Error fetching PPM data:', error);
      setIsLoadingPPMChart(false);
      setPpmDataError(true);
    }
  };

  useEffect(() => {
    setIsLoadingPPMChart(false);
    setPpmDataError(false);
    fetchDataForSelectedSize(); // Call this function whenever selectedSize changes
  }, [selectedSize]); // Only re-run the effect if selectedSize changes !!!



  useEffect(() => {
    console.log("Checking ppmChartData.series[0].data:", ppmChartData.series[0].data);
  }, [ppmChartData]);

  return (
    <div className="App">
      <div className="content">
        <div className="left-section">
          <div className="user-selection-section">
            <div className="selection-row">I am looking to</div>
            <div className="selection-row">
              <button onClick={() => handleButtonClick('Rent')} className={getButtonClass('Rent')}>Rent</button>
            </div>
            <div className="selection-row">
              <button onClick={() => handleButtonClick('Buy')} className={getButtonClass('Buy')}>Buy</button>
            </div>
            <div className="selection-row">a property in</div>
            <div className="selection-row">
              <select id="city-select" onChange={handleSelectChange} value={selection.location} className={isSelectedClass(selection.location)}>
                <option value="">City...</option>
                {cityData.cities.map((city, index) => (
                  <option key={index} value={city}>{city}</option>
                ))}
              </select>
            </div>
            {/* Conditionally render this next div based on whether provinces are available for the selected city */}
            {selection.location && cityData.provinces[selection.location]?.length > 0 && (
              <div className="selection-row">
                <select id="province-select" onChange={(e) => setProvince(e.target.value)} value={province} className={isSelectedClass(province)}>
                  <option value="">Province...</option>
                  {cityData.provinces[selection.location].map((provinceName, index) => (
                    <option key={index} value={provinceName}>{provinceName}</option>
                  ))}
                </select>
              </div>
            )}
            {/* Conditional rendering for the "See Prices" button */}
            {selection.action && selection.location && 
              (!cityData.provinces[selection.location] || cityData.provinces[selection.location].length === 0 || province) && (
                <div className="selection-row">
                  <button className="search-button fade-in" onClick={handleSeePricesClick}>See Prices!</button>
                </div>
            )}
          </div>
          {showChart && (
            <div className="input-container">
              <h2 className="price-check-title">Price Check</h2>
              <div className="input-group">
                <input
                  type="number"
                  style={inputStyle}
                  className="input-box"
                  value={squareMeters}
                  onChange={(e) => setSquareMeters(e.target.value)}
                />
                <span className="input-symbol">m²</span>
              </div>

              <div className="input-group" style={{ marginBottom: 0 }}>
                <input
                  type="number"
                  style={inputStyle}
                  className="input-box"
                  value={euros}
                  onChange={(e) => setEuros(e.target.value)}
                />
                <span className="input-symbol">€</span>
              </div>


              <button className="search-button" onClick={handleEvaluateClick}>Evaluate!</button>
            </div>
          )}

        </div>

        {/* Content below "See Prices!" button only appears after it's clicked */}
        {showChart && (
          <>
            <div className="chart-and-ppm-container">
              <div className="chart-container">
                {isLoadingChart  ? (
                  <div className="chart-loading-placeholder">l  o  a  d  i  n  g
                    <div className="reflection"></div> {/* This div creates the moving reflection effect */}
                  </div>  
                ) : (
                  <ReactApexChart 
                    options={chartData.options}
                    series={chartData.series}
                    type="area"
                    height='100%'
                  />
                )}
              </div>
              
              <hr className="hr-style" />

              {/* Conditional rendering for the size dropdown based on isLoading */}
              {!isLoadingPPMChart  && (
                
                <div className="size-selector"> 
                  <select value={selectedSize} onChange={(e) => setSelectedSize(e.target.value)}>
                    {generateSizeOptions()}
                  </select>
                </div>
              )}

              <div className="chart-container-2" ref={chartRef}>
                {isLoadingPPMChart ? (
                  <div className="chart-loading-placeholder">l o a d i n g
                    <div className="reflection-2"></div>
                  </div>
                ) : ppmDataError || ppmChartData.series[0].data.length === 0 ? ( // Check if error or no data
                  <div className="no-data-placeholder">no   data   available</div>
                ) : (
                  <ReactApexChart 
                    options={ppmChartData.options}
                    series={ppmChartData.series} 
                    type="area"
                    height='100%'
                  />
                )}
              </div>

              {/* Displaying the price per square meter below the chart */}
              {ppmValue && (
                <div className="ppm-display">
                  <p className='ppm-value-title'>Average Price:</p>
                  <p>{ppmValue}</p>
                  <p className='ppm-value-title'>€/m²</p>
                </div>
              )}

              {/* Display the result of the evaluation below the ppmValue */}
              {eurosPerSqMeter && (
                <div className={`evaluation-result ${percentageDifference > 0 ? 'text-red' : 'text-green'}`}>
                  <p className={`ppm-value-title-a ${percentageDifference > 0 ? 'text-red-small' : 'text-green-small'}`}>Evaluation:</p>
                  <h3>{eurosPerSqMeter}</h3>
                  <p className={`ppm-value-title-a ${percentageDifference > 0 ? 'text-red-small' : 'text-green-small'}`}>€/m²</p>
                </div>
              )}

              {/* Conditional rendering for percentage difference */}
              <div className={`evaluation-summary ${percentageDifference > 0 ? 'text-red' : 'text-green'}`}>
                {percentageDifference && (
                  <p>
                    {parseFloat(percentageDifference) > 0 ? `Higher than Average by ${percentageDifference}%` : `Lower than Average by ${Math.abs(percentageDifference)}%`}
                  </p>
                )}
              </div>

            </div>
          </>
        )}
      </div>
    </div>
  );
}
export default App;
