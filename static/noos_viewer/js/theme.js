(function ($) {
    "use strict"; // Start of use strict

    $("a").each(function () {
        if ($(this).attr("href").length > 5) {
            var a_href_ext1 = $(this).attr("href").substr(-2);
            var a_href_ext2 = $(this).attr("href").substr(-3);
            var a_href_ext3 = $(this).attr("href").substr(-4);
            var a_href_ext4 = $(this).attr("href").substr(-5);

            if (a_href_ext3 === ".pdf" || a_href_ext3 === ".PDF") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-pdf\" style=\"color:red;\"></i>";
                    else
                        return "<i class=\"fas fa-file-pdf\" style=\"color:red;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "darkred");
                }, function () {
                    $(this).find("i").css("color", "red");
                });
            }

            if (a_href_ext3 === ".doc" || a_href_ext4 === ".docx" || a_href_ext3 === ".DOC" || a_href_ext4 === ".DOCX") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-word\" style=\"color:dodgerblue;\"></i>";
                    else
                        return "<i class=\"fas fa-file-word\" style=\"color:dodgerblue;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "blue");
                }, function () {
                    $(this).find("i").css("color", "dodgerblue");
                });
            }

            if (a_href_ext3 === ".xls" || a_href_ext4 === ".xlsx" || a_href_ext3 === ".XLS" || a_href_ext4 === ".XLSX") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-excel\" style=\"color:forestgreen;\"></i>";
                    else
                        return "<i class=\"fas fa-file-excel\" style=\"color:forestgreen;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "darkgreen");
                }, function () {
                    $(this).find("i").css("color", "forestgreen");
                });
            }

            if (a_href_ext3 === ".ppt" || a_href_ext4 === ".pptx" || a_href_ext3 === ".PPT" || a_href_ext4 === ".PPTX") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-powerpoint\" style=\"color:orangered;\"></i>";
                    else
                        return "<i class=\"fas fa-file-powerpoint\" style=\"color:orangered;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "darkred");
                }, function () {
                    $(this).find("i").css("color", "orangered");
                });
            }

            if (a_href_ext3 === ".odt" || a_href_ext3 === ".rtf" || a_href_ext3 === ".ODT" || a_href_ext3 === ".RTF") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-alt\" style=\"color:dodgerblue;\"></i>";
                    else
                        return "<i class=\"fas fa-file-alt\" style=\"color:dodgerblue;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "blue");
                }, function () {
                    $(this).find("i").css("color", "dodgerblue");
                });
            }

            if (a_href_ext3 === ".ods" || a_href_ext3 === ".ODS") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-alt\" style=\"color:forestgreen;\"></i>";
                    else
                        return "<i class=\"fas fa-file-alt\" style=\"color:forestgreen;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "darkgreen");
                }, function () {
                    $(this).find("i").css("color", "forestgreen");
                });
            }

            if (a_href_ext3 === ".txt" || a_href_ext3 === ".TXT") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-alt\" style=\"color:lightgrey;\"></i>";
                    else
                        return "<i class=\"fas fa-file-alt\" style=\"color:lightgrey;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "dimgrey");
                }, function () {
                    $(this).find("i").css("color", "lightgrey");
                });
            }

            if (a_href_ext3 === ".csv" || a_href_ext3 === ".CSV") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-csv\" style=\"color:lightgrey;\"></i>";
                    else
                        return "<i class=\"fas fa-file-csv\" style=\"color:lightgrey;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "dimgrey");
                }, function () {
                    $(this).find("i").css("color", "lightgrey");
                });
            }

            if (a_href_ext1 === ".z" || a_href_ext2 === ".gz" || a_href_ext2 === ".lz" || a_href_ext2 === ".xz" || a_href_ext2 === ".7z" || a_href_ext2 === ".zz" || a_href_ext3 === ".zip" || a_href_ext3 === ".tar" || a_href_ext3 === ".bz2" || a_href_ext3 === ".jar" || a_href_ext3 === ".apk" || a_href_ext3 === ".s7z" || a_href_ext3 === ".cab" || a_href_ext3 === ".dmg" || a_href_ext3 === ".rar" || a_href_ext3 === ".sfx" || a_href_ext3 === ".war" || a_href_ext3 === ".tgz" || a_href_ext3 === ".txz" || a_href_ext3 === ".tlz" || a_href_ext4 === ".lzma" || a_href_ext4 === ".zipx" || a_href_ext4 === ".tbz2" || a_href_ext1 === ".Z" || a_href_ext2 === ".GZ" || a_href_ext2 === ".LZ" || a_href_ext2 === ".XZ" || a_href_ext2 === ".7Z" || a_href_ext2 === ".ZZ" || a_href_ext3 === ".ZIP" || a_href_ext3 === ".TAR" || a_href_ext3 === ".BZ2" || a_href_ext3 === ".JAR" || a_href_ext3 === ".APK" || a_href_ext3 === ".S7Z" || a_href_ext3 === ".CAB" || a_href_ext3 === ".DMG" || a_href_ext3 === ".RAR" || a_href_ext3 === ".SFX" || a_href_ext3 === ".WAR" || a_href_ext3 === ".TGZ" || a_href_ext3 === ".TXZ" || a_href_ext3 === ".TLZ" || a_href_ext4 === ".LZMA" || a_href_ext4 === ".ZIPX" || a_href_ext4 === ".TBZ2") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-archive\" style=\"color:darkorange;\"></i>";
                    else
                        return "<i class=\"fas fa-file-archive\" style=\"color:darkorange;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "#ab5600");
                }, function () {
                    $(this).find("i").css("color", "darkorange");
                });
            }

            if (a_href_ext3 === ".gif" || a_href_ext3 === ".jpg" || a_href_ext3 === ".jp2" || a_href_ext3 === ".jpx" || a_href_ext3 === ".bmp" || a_href_ext3 === ".png" || a_href_ext3 === ".bpg" || a_href_ext3 === ".svg" || a_href_ext4 === ".jpeg" || a_href_ext4 === ".tiff" || a_href_ext4 === ".webp" || a_href_ext4 === ".heif" || a_href_ext4 === ".heic" || a_href_ext3 === ".GIF" || a_href_ext3 === ".JPG" || a_href_ext3 === ".JP2" || a_href_ext3 === ".JPX" || a_href_ext3 === ".BMP" || a_href_ext3 === ".PNG" || a_href_ext3 === ".BPG" || a_href_ext3 === ".SVG" || a_href_ext4 === ".JPEG" || a_href_ext4 === ".TIFF" || a_href_ext4 === ".WEBP" || a_href_ext4 === ".HEIF" || a_href_ext4 === ".HEIC") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-image\" style=\"color:mediumpurple;\"></i>";
                    else
                        return "<i class=\"fas fa-file-image\" style=\"color:mediumpurple;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "purple");
                }, function () {
                    $(this).find("i").css("color", "mediumpurple");
                });
            }

            if (a_href_ext2 === ".rm" || a_href_ext2 === ".qt" || a_href_ext3 === ".avi" || a_href_ext3 === ".mov" || a_href_ext3 === ".mpa" || a_href_ext3 === ".asf" || a_href_ext3 === ".wma" || a_href_ext3 === ".mp2" || a_href_ext3 === ".m2p" || a_href_ext3 === ".vob" || a_href_ext3 === ".mkv" || a_href_ext3 === ".flv" || a_href_ext3 === ".ogv" || a_href_ext3 === ".ogg" || a_href_ext3 === ".mp4" || a_href_ext3 === ".m4p" || a_href_ext3 === ".m4v" || a_href_ext3 === ".3gp" || a_href_ext3 === ".mpe" || a_href_ext3 === ".mpv" || a_href_ext3 === ".mpg" || a_href_ext4 === ".webm" || a_href_ext4 === ".rmvb" || a_href_ext4 === ".mpeg" || a_href_ext2 === ".RM" || a_href_ext2 === ".QT" || a_href_ext3 === ".AVI" || a_href_ext3 === ".MOV" || a_href_ext3 === ".MPA" || a_href_ext3 === ".ASF" || a_href_ext3 === ".WMA" || a_href_ext3 === ".MP2" || a_href_ext3 === ".M2P" || a_href_ext3 === ".VOB" || a_href_ext3 === ".MKV" || a_href_ext3 === ".FLV" || a_href_ext3 === ".OGV" || a_href_ext3 === ".OGG" || a_href_ext3 === ".MP4" || a_href_ext3 === ".M4P" || a_href_ext3 === ".M4V" || a_href_ext3 === ".3GP" || a_href_ext3 === ".MPE" || a_href_ext3 === ".MPV" || a_href_ext3 === ".MPG" || a_href_ext4 === ".WEBM" || a_href_ext4 === ".RMVB" || a_href_ext4 === ".MPEG") {
                $(this).html(function (i, html) {
                    if ($(this).html().length === 0)
                        return "<i class=\"fas fa-file-video\" style=\"color:darkorange;\"></i>";
                    else
                        return "<i class=\"fas fa-file-video\" style=\"color:darkorange;\"></i>&nbsp;" + html;
                });
                $(this).hover(function () {
                    $(this).find("i").css("color", "#ab5600");
                }, function () {
                    $(this).find("i").css("color", "darkorange");
                });
            }
        }
    });
})(jQuery); // End of use strict