import 'package:flutter/material.dart';
import 'package:data_table_2/data_table_2.dart';
import 'widget_registry.dart';

/// 表格组件配置
class TableConfig extends ComponentConfig {
  final String title;
  final List<String> columns;
  final List<List<String>> rows;
  final bool showBorder;
  final bool sortable;

  TableConfig({
    required Map<String, dynamic> data,
    required Map<String, dynamic> config,
    required this.title,
    required this.columns,
    required this.rows,
    required this.showBorder,
    required this.sortable,
  }) : super(type: 'table', data: data, config: config);

  factory TableConfig.fromSchema(Map<String, dynamic> schema) {
    final data = schema['data'] as Map<String, dynamic>? ?? {};
    final config = schema['config'] as Map<String, dynamic>? ?? {};

    final columns = data.getList<String>('columns') ?? [];

    final rowsData = data['rows'] as List? ?? [];
    final rows = rowsData.map((row) {
      if (row is List) {
        return row.map((cell) => cell.toString()).toList();
      }
      return <String>[];
    }).toList();

    return TableConfig(
      data: data,
      config: config,
      title: data.getString('title') ?? '',
      columns: columns,
      rows: rows,
      showBorder: config.getBool('show_border') ?? true,
      sortable: config.getBool('sortable') ?? false,
    );
  }
}

class TableWidget extends StatefulWidget {
  final TableConfig config;

  const TableWidget({
    super.key,
    required this.config,
  });

  static Widget fromSchema(Map<String, dynamic> schema) {
    final config = TableConfig.fromSchema(schema);
    return TableWidget(config: config);
  }

  @override
  State<TableWidget> createState() => _TableWidgetState();
}

class _TableWidgetState extends State<TableWidget> {
  int? _sortColumnIndex;
  bool _sortAscending = true;
  late List<List<String>> _sortedRows;

  @override
  void initState() {
    super.initState();
    _sortedRows = List.from(widget.config.rows);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (widget.config.title.isNotEmpty) ...[
              Text(
                widget.config.title,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
            ],
            if (widget.config.columns.isEmpty || _sortedRows.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text(
                    '暂无数据',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              )
            else
              SizedBox(
                height: 400,
                child: DataTable2(
                  columnSpacing: 12,
                  horizontalMargin: 12,
                  minWidth: 600,
                  border: widget.config.showBorder
                      ? TableBorder.all(
                          color: theme.dividerColor,
                          width: 1,
                        )
                      : null,
                  sortColumnIndex: _sortColumnIndex,
                  sortAscending: _sortAscending,
                  columns: widget.config.columns.asMap().entries.map((entry) {
                    final index = entry.key;
                    final column = entry.value;
                    return DataColumn2(
                      label: Text(
                        column,
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      onSort: widget.config.sortable
                          ? (columnIndex, ascending) {
                              _sortRows(columnIndex, ascending);
                            }
                          : null,
                    );
                  }).toList(),
                  rows: _sortedRows.map((row) {
                    return DataRow2(
                      cells: row.map((cell) {
                        return DataCell(
                          Text(
                            cell,
                            style: theme.textTheme.bodyMedium,
                          ),
                        );
                      }).toList(),
                    );
                  }).toList(),
                ),
              ),
          ],
        ),
      ),
    );
  }

  void _sortRows(int columnIndex, bool ascending) {
    setState(() {
      _sortColumnIndex = columnIndex;
      _sortAscending = ascending;

      _sortedRows.sort((a, b) {
        if (columnIndex >= a.length || columnIndex >= b.length) {
          return 0;
        }

        final aValue = a[columnIndex];
        final bValue = b[columnIndex];

        // Try to parse as numbers
        final aNum = num.tryParse(aValue);
        final bNum = num.tryParse(bValue);

        int comparison;
        if (aNum != null && bNum != null) {
          comparison = aNum.compareTo(bNum);
        } else {
          comparison = aValue.compareTo(bValue);
        }

        return ascending ? comparison : -comparison;
      });
    });
  }
}
