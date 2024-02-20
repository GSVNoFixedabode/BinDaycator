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

//echo $json;

// Decoding JSON to PHP array
$data = json_decode($json, true);
echo "Data ";
echo $data;

// Accessing the collections data
$collections = $data['bins']['collections'];

// Calculate 7 days from now
$sevenDaysFromNow = strtotime('+7 days');

// Filter bins for next 7 days
$currentOrFutureBins = array_filter($collections, function ($collection) use ($sevenDaysFromNow) {
    $nextPlannedDate = strtotime($collection['next_planned_date']);
    return $nextPlannedDate <= $sevenDaysFromNow;
});
// Displaying filtered bins
echo "Filtered Bins:\n";
foreach ($currentOrFutureBins as $bin) {
    echo "- Next Planned Date: {$bin['next_planned_date']}, Material: {$bin['material']}, Pick Up Group: {$bin['pick_up_group']}, Out of Date: {$bin['out_of_date']}\n";
}
// Return JSON response
header('Content-Type: application/json');
echo json_encode($response);

?>
