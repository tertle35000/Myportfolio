SELECT TOP (50000) [id]
      ,[Item Number]
      ,[Parameter]
      ,[Address]
      ,[Value]
      ,[Status]
      ,[Type]
      ,[DataTime]
  FROM [MyDatabase].[dbo].[MiniProject-(table2)]

CREATE VIEW VoltageView AS
SELECT id, [Item Number], Parameter, Address, Value, Status, Type, DataTime
FROM [MiniProject-(table2)]
WHERE Parameter = 'Voltage';
SELECT * FROM VoltageView;

CREATE VIEW CurrentView AS
SELECT id, [Item Number], Parameter, Address, Value, Status, Type, DataTime
FROM [MiniProject-(table2)]
WHERE Parameter = 'Current';
SELECT * FROM CurrentView;

CREATE VIEW MotorView AS
SELECT id, [Item Number], Parameter, Address, Value, Status, Type, DataTime
FROM [MiniProject-(table2)]
WHERE Parameter = 'Motor';
SELECT * FROM MotorView;