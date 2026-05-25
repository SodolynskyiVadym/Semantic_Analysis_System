using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Serialization;

namespace ClientApp.Models
{
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public enum EntityType
    {
        [JsonPropertyName("QUANTITY")]
        Quantity,

        [JsonPropertyName("LOCATION")]
        Location,

        [JsonPropertyName("PERSONNEL-FRIENDLY")]
        PersonnelFriendly,

        [JsonPropertyName("PERSONNEL-ENEMY")]
        PersonnelEnemy,

        [JsonPropertyName("EQUIPMENT-FRIENDLY")]
        EquipmentFriendly,

        [JsonPropertyName("EQUIPMENT-ENEMY")]
        EquipmentEnemy
    }
}
