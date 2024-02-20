<?php
// Check if the ID is provided as a command-line argument ID should be 82918
// Retrieve the variable passed in the URL
$raw_input = $_GET['propertyid'];

// Sanitise
function sanitizeInput($input) {
    // Remove any non-numeric characters
    $sanitized_input = preg_replace("/[^0-9]/", "", $input);

    // Check if the sanitized input is exactly 5 digits long
    if(strlen($sanitized_input) === 5) {
        return $sanitized_input;
    } else {
        return false; // Return false if the input is not a 5-digit number
    }
}

$propertyid = sanitizeInput($raw_input);
if($propertyid == false) {
    exit("Invalid input!");
}

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
