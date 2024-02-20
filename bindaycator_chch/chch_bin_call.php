<?php

// Check if the ID is provided as a command-line argument ID should be 82918
// Retrieve the variable passed in the URL
$propertyid = $_GET['propertyid'];

// Get the ID from the command-line argument
//$id = urlencode($argv[1]);

// URL of the API with the ID parameter
$url = "https://www.ccc.govt.nz/services/rubbish-and-recycling/collections/getProperty?ID=$propertyid";

// Fetching JSON
$curl = curl_init($url);
curl_setopt($curl, CURLOPT_URL, $url);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
$json = curl_exec($curl);
curl_close($curl);

// Decoding JSON to PHP array
$data = json_decode($json, true);


// Get the current date and 7 days from now
$currentDate = strtotime(date('Y-m-d'));
$sevenDaysFromNow = strtotime('+7 days');

// Loop through collections and filter by date
$filteredCollections = [];
foreach ($data['bins']['collections'] as $collection) {
    $nextPlannedDate = strtotime($collection['next_planned_date']);
    if ($nextPlannedDate >= $currentDate && $nextPlannedDate <= $sevenDaysFromNow) {
        $filteredCollections[] = [
            'material' => $collection['material'],
            'next_planned_date' => $collection['next_planned_date']
        ];
    }
}

// Return the filtered collections as JSON
header('Content-Type: application/json');
echo json_encode($filteredCollections);