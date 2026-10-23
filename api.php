<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json; charset=UTF-8");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

$dataFile = __DIR__ . '/isg_ziyaretciler.json';

function getStoredData($file) {
    if (!file_exists($file)) return [];
    $content = file_get_contents($file);
    return json_decode($content, true) ?: [];
}

function saveStoredData($file, $data) {
    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

$action = $_GET['action'] ?? '';
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    $raw = file_get_contents('php://input');
    $input = json_decode($raw, true) ?: [];

    if ($action === 'ziyaretci-cikis' || (isset($input['action']) && $input['action'] === 'ziyaretci-cikis')) {
        $tracking = $input['tracking_code'] ?? '';
        $outTime = $input['check_out_time'] ?? date('c');

        $records = getStoredData($dataFile);
        $updated = false;
        foreach ($records as &$item) {
            if (($item['tracking_code'] ?? '') === $tracking) {
                $item['status'] = 'Çıkış Yapıldı';
                $item['check_out_time'] = $outTime;
                $updated = true;
                break;
            }
        }
        saveStoredData($dataFile, $records);
        echo json_encode(['status' => 'success', 'updated' => $updated]);
        exit();
    }

    $trackingCode = $input['tracking_code'] ?? ('ISG-2026-' . rand(1000, 9999));
    $input['tracking_code'] = $trackingCode;
    $input['hazard_class'] = $input['hazard_class'] ?? 'Az Tehlikeli';
    $input['ppe_items'] = $input['ppe_items'] ?? '';
    
    // Dijital İSG taahhüt hash'i
    $rawPayload = "ISG-TERMS-6331|TC:".($input['visitor_id'] ?? '')."|NAME:".strtoupper($input['visitor_name'] ?? '')."|TEL:".($input['visitor_phone'] ?? '')."|HAZARD:".$input['hazard_class']."|TIME:".($input['check_in_time'] ?? '');
    $digitalHash = hash('sha256', $rawPayload);
    $input['digital_signature_hash'] = $digitalHash;
    $input['status'] = $input['status'] ?? 'Tesis İçinde (Aktif)';
    $input['created_at'] = $input['created_at'] ?? date('c');

    $records = getStoredData($dataFile);
    array_unshift($records, $input);
    saveStoredData($dataFile, $records);

    echo json_encode([
        'status' => 'success',
        'tracking_code' => $trackingCode,
        'digital_signature_hash' => $digitalHash,
        'hazard_class' => $input['hazard_class']
    ], JSON_UNESCAPED_UNICODE);
    exit();
}

if ($method === 'GET') {
    $records = getStoredData($dataFile);

    if ($action === 'acil-tahliye') {
        $inside = array_values(array_filter($records, function($r) {
            return ($r['status'] ?? 'Tesis İçinde (Aktif)') === 'Tesis İçinde (Aktif)';
        }));
        echo json_encode([
            'status' => 'success',
            'report' => [
                'total_inside_count' => count($inside),
                'generated_at' => date('d.m.Y H:i:s'),
                'active_visitors' => $inside
            ]
        ], JSON_UNESCAPED_UNICODE);
        exit();
    }

    echo json_encode($records, JSON_UNESCAPED_UNICODE);
    exit();
}
