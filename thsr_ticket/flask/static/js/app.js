document.addEventListener('DOMContentLoaded', function() {
    // 初始化 flatpickr
    flatpickr("#travel_date", {
        minDate: "today",
        maxDate: new Date().fp_incr(30) // 30 days from now
    });

    $.getJSON('/api/data', function(data) {
        console.log('Data received:', data);
        var tableBody = $('#data-table tbody');
        tableBody.empty(); // 清空表格內容

        data.forEach(function(record) {
            var maskedPersonalId = maskPersonalId(record.personal_id);
            var row = '<tr>' +
                '<td>' + record.id + '</td>' +
                '<td>' + record.adult_num + '</td>' +
                '<td>' + record.start_station + '</td>' +
                '<td>' + record.dest_station + '</td>' +
                '<td>' + record.email + '</td>' +
                '<td>' + record.outbound_date + '</td>' +
                '<td>' + record.outbound_time + '</td>' +
                '<td>' + maskedPersonalId + '</td>' +
                '<td>' + record.phone + '</td>' +
                '<td>' + record.selection_time + '</td>' +
                '</tr>';
            tableBody.append(row);
        });

        $('#loading').hide(); // 隱藏加載訊息
    }).fail(function(jqxhr, textStatus, error) {
        console.error('Error fetching data:', textStatus, error);
        $('#loading').text('Failed to load data');
    });

    function maskPersonalId(personal_ids) {
        if (!Array.isArray(personal_ids)) return '';
        return personal_ids.map(personal_id => {
            if (personal_id.length <= 3) {
                return personal_id.slice(0, 3) + '*'.repeat(0);
            }
            return personal_id.slice(0, 3) + '*'.repeat(personal_id.length - 3);
        }).join(', ');
    }
});